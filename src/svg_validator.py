#!/usr/bin/env python3
"""
SVG Validation Wrapper: Centralizes all SVG validation and fixing operations
"""

from pathlib import Path
from typing import Optional, Union, Callable, Any, Tuple, List
import functools
import logging

logger = logging.getLogger(__name__)

def validate_svg_operation(backup_on_edit: bool = True, fix_on_fail: bool = True):
    """
    Decorator that wraps SVG operations with validation.
    
    Args:
        backup_on_edit: Create version backup before modification
        fix_on_fail: Attempt to fix common XML issues if validation fails
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from svg_packager import validate_and_fix_svg, _backup_current_version
            
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Try to extract SVG path from result or arguments
            svg_path = None
            
            # Check if result contains SVG path (for functions returning tuples)
            if isinstance(result, tuple) and len(result) >= 1:
                potential_path = result[0]
                if isinstance(potential_path, (str, Path)) and str(potential_path).endswith('.svg'):
                    svg_path = Path(potential_path)
            
            # Check arguments for SVG path
            if svg_path is None:
                for arg in args:
                    if isinstance(arg, (str, Path)) and str(arg).endswith('.svg'):
                        svg_path = Path(arg)
                        break
                
                # Check keyword arguments
                if svg_path is None:
                    for key, value in kwargs.items():
                        if 'svg' in key.lower() and isinstance(value, (str, Path)):
                            svg_path = Path(value)
                            break
            
            # Validate if we found an SVG path
            if svg_path and svg_path.exists():
                logger.info(f"Validating SVG after operation: {svg_path}")
                
                if fix_on_fail:
                    is_valid, errors = validate_and_fix_svg(svg_path)
                else:
                    from svg_packager import _validate_svg
                    is_valid, errors = _validate_svg(svg_path)
                
                # Log validation results
                if is_valid:
                    logger.info(f"✓ SVG validation passed: {svg_path}")
                else:
                    logger.warning(f"⚠ SVG validation failed: {svg_path}")
                    for error in errors:
                        logger.warning(f"  - {error}")
                
                # Return enhanced result with validation info
                if isinstance(result, tuple):
                    return result + (is_valid, errors)
                else:
                    return result, is_valid, errors
            
            return result
        return wrapper
    return decorator


class SVGOperationManager:
    """
    Context manager for SVG operations with comprehensive validation and backup.
    """
    
    def __init__(self, svg_path: Union[str, Path], 
                 backup_before_edit: bool = True,
                 validate_after_edit: bool = True,
                 fix_issues: bool = True):
        self.svg_path = Path(svg_path)
        self.backup_before_edit = backup_before_edit
        self.validate_after_edit = validate_after_edit
        self.fix_issues = fix_issues
        self.backup_created = False
        self.validation_results: Optional[Tuple[bool, List[str]]] = None
        
    def __enter__(self):
        if self.backup_before_edit and self.svg_path.exists():
            from svg_packager import _backup_current_version
            _backup_current_version(self.svg_path.parent, self.svg_path)
            self.backup_created = True
            logger.info(f"Created backup before editing: {self.svg_path}")
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.validate_after_edit and self.svg_path.exists():
            if self.fix_issues:
                from svg_packager import validate_and_fix_svg
                is_valid, errors = validate_and_fix_svg(self.svg_path)
            else:
                from svg_packager import _validate_svg
                is_valid, errors = _validate_svg(self.svg_path)
            
            self.validation_results = (is_valid, errors)
            
            if is_valid:
                logger.info(f"✓ SVG validation passed after edit: {self.svg_path}")
            else:
                logger.warning(f"⚠ SVG validation failed after edit: {self.svg_path}")
                for error in errors:
                    logger.warning(f"  - {error}")
    
    def get_validation_results(self) -> Optional[Tuple[bool, List[str]]]:
        """Get the validation results from the last operation."""
        return self.validation_results


def validate_all_project_svgs(project_dir: Union[str, Path]) -> dict:
    """
    Validate all SVG files in a project directory.
    
    Returns:
        dict: {svg_filename: (is_valid, errors)}
    """
    from svg_packager import validate_and_fix_svg
    
    project_path = Path(project_dir)
    results = {}
    
    # Check main SVG
    for svg_file in project_path.glob('*.svg'):
        is_valid, errors = validate_and_fix_svg(svg_file)
        results[svg_file.name] = (is_valid, errors)
    
    # Check version SVGs
    versions_dir = project_path / 'versions'
    if versions_dir.exists():
        for svg_file in versions_dir.glob('*.svg'):
            is_valid, errors = validate_and_fix_svg(svg_file)
            results[f"versions/{svg_file.name}"] = (is_valid, errors)
    
    # Summary logging
    total_files = len(results)
    valid_files = sum(1 for is_valid, _ in results.values() if is_valid)
    
    logger.info(f"Validated {total_files} SVG files in {project_path}")
    logger.info(f"Valid: {valid_files}, Invalid: {total_files - valid_files}")
    
    return results


def batch_fix_svg_issues(project_dir: Union[str, Path]) -> dict:
    """
    Batch fix common SVG issues in all project files.
    
    Returns:
        dict: {svg_filename: (was_fixed, is_now_valid, errors)}
    """
    from svg_packager import _validate_svg, _fix_common_xml_issues
    
    project_path = Path(project_dir)
    results = {}
    
    def fix_svg_file(svg_path: Path) -> Tuple[bool, bool, List[str]]:
        # Initial validation
        initial_valid, initial_errors = _validate_svg(svg_path)
        if initial_valid:
            return False, True, []  # No fix needed
        
        # Attempt fix
        content = svg_path.read_text(encoding='utf-8')
        fixed_content = _fix_common_xml_issues(content)
        
        if fixed_content != content:
            # Create backup before fixing
            from svg_packager import _backup_current_version
            _backup_current_version(svg_path.parent, svg_path)
            
            # Write fixed content
            svg_path.write_text(fixed_content, encoding='utf-8')
            
            # Validate after fix
            final_valid, final_errors = _validate_svg(svg_path)
            return True, final_valid, final_errors
        else:
            return False, False, initial_errors
    
    # Fix main SVGs
    for svg_file in project_path.glob('*.svg'):
        was_fixed, is_valid, errors = fix_svg_file(svg_file)
        results[svg_file.name] = (was_fixed, is_valid, errors)
    
    # Fix version SVGs
    versions_dir = project_path / 'versions'
    if versions_dir.exists():
        for svg_file in versions_dir.glob('*.svg'):
            was_fixed, is_valid, errors = fix_svg_file(svg_file)
            results[f"versions/{svg_file.name}"] = (was_fixed, is_valid, errors)
    
    return results


# Pre-configured decorators for common operations
svg_generation_validator = validate_svg_operation(backup_on_edit=False, fix_on_fail=True)
svg_edit_validator = validate_svg_operation(backup_on_edit=True, fix_on_fail=True)
svg_strict_validator = validate_svg_operation(backup_on_edit=True, fix_on_fail=False)
