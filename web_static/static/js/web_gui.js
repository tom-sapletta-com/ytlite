document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        updateThemeButton(savedTheme);
    } else {
        // Check system preference
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = systemPrefersDark ? 'dark' : 'light';
        document.body.setAttribute('data-theme', initialTheme);
        updateThemeButton(initialTheme);
    }
    
    // Check for saved view preference
    const savedView = localStorage.getItem('viewMode');
    if (savedView) {
        setViewMode(savedView);
    } else {
        setViewMode('grid'); // Default to grid view
    }
    
    // Toggle between grid and table view
    document.getElementById('view-toggle').addEventListener('click', function() {
        const projectsList = document.getElementById('projectsList');
        if (projectsList.classList.contains('projects-grid')) {
            projectsList.classList.remove('projects-grid');
            projectsList.classList.add('table-view');
            this.textContent = 'Grid View';
        } else {
            projectsList.classList.remove('table-view');
            projectsList.classList.add('projects-grid');
            this.textContent = 'Table View';
        }
        localStorage.setItem('viewMode', projectsList.classList.contains('projects-grid') ? 'grid' : 'table');
        loadProjects();
    });
});

function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (theme === 'dark') {
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light Mode';
    } else {
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark Mode';
    }
}

function showCreateForm() {
    document.getElementById('create-form').style.display = 'block';
    document.getElementById('projects-list').style.display = 'none';
}

function showProjectsList() {
    document.getElementById('create-form').style.display = 'none';
    document.getElementById('projects-list').style.display = 'block';
    loadProjects();
}

function toggleViewMode() {
    const currentView = localStorage.getItem('viewMode') || 'grid';
    const newView = currentView === 'grid' ? 'table' : 'grid';
    setViewMode(newView);
}

function setViewMode(view) {
    const container = document.getElementById('projectsList');
    const toggleButton = document.getElementById('view-toggle');
    
    if (view === 'grid') {
        container.className = 'projects-grid';
        toggleButton.textContent = 'Switch to Table View';
    } else {
        container.className = 'table-view';
        toggleButton.textContent = 'Switch to Grid View';
    }
    
    localStorage.setItem('viewMode', view);
    loadProjects();
}

async function loadProjects() {
    try {
        const res = await fetch('/api/projects');
        const data = await res.json();
        const container = document.getElementById('projectsList');
        const viewMode = localStorage.getItem('viewMode') || 'grid';
        
        container.innerHTML = '';
        
        if (viewMode === 'grid') {
            data.projects.forEach(project => {
                const card = document.createElement('div');
                card.className = 'project-card';
                card.onclick = () => showProjectDetails(project.name);
                
                card.innerHTML = `
                    <div class="project-title">${project.name}</div>
                    <div class="project-meta">
                        ${project.type === 'svg' ? 
                            `<span>${project.metadata.title || 'SVG Project'}</span>` : 
                            `<span>Directory Project</span>`}
                    </div>
                    <div class="project-actions">
                        <button class="btn btn-primary" onclick="event.stopPropagation(); editProject('${project.name}')">Edit</button>
                        <button class="btn" onclick="event.stopPropagation(); showVersionHistory('${project.name}')">History</button>
                        <button class="btn btn-danger" onclick="event.stopPropagation(); deleteProject('${project.name}')">Delete</button>
                        <button class="btn" onclick="event.stopPropagation(); publishToWordPress('${project.name}')">Publish to WordPress</button>
                    </div>
                `;
                container.appendChild(card);
            });
        } else {
            const table = document.createElement('table');
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Project Name</th>
                        <th>Type</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            `;
            const tbody = table.querySelector('tbody');
            
            data.projects.forEach(project => {
                const row = document.createElement('tr');
                row.onclick = () => showProjectDetails(project.name);
                row.innerHTML = `
                    <td>${project.name}</td>
                    <td>${project.type === 'svg' ? (project.metadata.title || 'SVG Project') : 'Directory Project'}</td>
                    <td>
                        <button class="btn btn-primary" onclick="event.stopPropagation(); editProject('${project.name}')">Edit</button>
                        <button class="btn" onclick="event.stopPropagation(); showVersionHistory('${project.name}')">History</button>
                        <button class="btn btn-danger" onclick="event.stopPropagation(); deleteProject('${project.name}')">Delete</button>
                        <button class="btn" onclick="event.stopPropagation(); publishToWordPress('${project.name}')">Publish to WordPress</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            container.appendChild(table);
        }
    } catch (err) {
        showMessage('Failed to load projects', 'error');
        console.error(err);
    }
}

async function editProject(name) {
    try {
        const res = await fetch(`/api/svg_meta?project=${name}`);
        if (res.ok) {
            const meta = await res.json();
            document.getElementById('project').value = name;
            if (meta.markdown) {
                document.getElementById('markdown').value = meta.markdown;
            }
            if (meta.voice) {
                document.getElementById('voice').value = meta.voice;
            }
            if (meta.theme) {
                document.getElementById('theme').value = meta.theme;
            }
            showCreateForm();
        } else {
            showMessage('Failed to load project data', 'error');
        }
    } catch (err) {
        showMessage('Error loading project', 'error');
        console.error(err);
    }
}

function showProjectDetails(projectName) {
    // Placeholder for project details view
    showMessage(`Viewing details for ${projectName}`, 'info');
}

async function generate() {
    const project = document.getElementById('project').value.trim();
    const markdown = document.getElementById('markdown').value;
    const voice = document.getElementById('voice').value;
    const theme = document.getElementById('theme').value;
    
    if (!project || !markdown) {
        showMessage('Please enter project name and markdown content', 'error');
        return;
    }
    
    try {
        showMessage('Generating video...', 'info');
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project, markdown, voice, theme })
        });
        
        const data = await res.json();
        if (res.ok) {
            showMessage(`Video generated: ${data.video_path}`, 'success');
            showProjectsList();
        } else {
            showMessage(`Error: ${data.message}`, 'error');
        }
    } catch (err) {
        showMessage('Failed to generate video', 'error');
        console.error(err);
    }
}

async function showVersionHistory(projectName) {
    try {
        const res = await fetch(`/api/project_history?project=${encodeURIComponent(projectName)}`);
        const history = await res.json();
        
        const container = document.getElementById('projectsList');
        container.innerHTML = `<button class="btn" onclick="showProjectsList()">Back to Projects</button>
        <h2>Version History for ${projectName}</h2>
        <div class="version-history"></div>`;
        
        const historyContainer = container.querySelector('.version-history');
        if (history.versions && history.versions.length > 0) {
            history.versions.forEach(version => {
                const versionItem = document.createElement('div');
                versionItem.className = 'version-item';
                versionItem.innerHTML = `
                    <span>Version from ${version.date}</span>
                    <button class="btn btn-primary" onclick="event.stopPropagation(); restoreVersion('${projectName}', '${version.file}')">Restore</button>
                `;
                historyContainer.appendChild(versionItem);
            });
        } else {
            historyContainer.innerHTML = '<p>No version history available.</p>';
        }
    } catch (err) {
        showMessage('Failed to load version history', 'error');
        console.error(err);
    }
}

async function restoreVersion(projectName, versionFile) {
    try {
        const res = await fetch(`/api/restore_version`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project: projectName, version: versionFile })
        });
        
        if (res.ok) {
            showMessage(`Version restored for ${projectName}`, 'success');
            showProjectsList();
        } else {
            const data = await res.json();
            showMessage(`Failed to restore version: ${data.message}`, 'error');
        }
    } catch (err) {
        showMessage('Error restoring version', 'error');
        console.error(err);
    }
}

async function deleteProject(projectName) {
    if (!confirm(`Are you sure you want to delete ${projectName}? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const res = await fetch(`/api/delete_project`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project: projectName })
        });
        
        if (res.ok) {
            showMessage(`${projectName} deleted successfully`, 'success');
            loadProjects();
        } else {
            const data = await res.json();
            showMessage(`Failed to delete ${projectName}: ${data.message}`, 'error');
        }
    } catch (err) {
        showMessage('Error deleting project', 'error');
        console.error(err);
    }
}

async function publishToWordPress(projectName, event) {
    if (event) event.stopPropagation();
    
    showMessage('📝 Publishing to WordPress...', 'info');
    
    try {
        const res = await fetch('/api/publish/wordpress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project: projectName })
        });
        
        const data = await res.json();
        if (res.ok) {
            showMessage(`✅ Published to WordPress: <a href="${data.url}" target="_blank">View Post</a>`, 'success');
        } else {
            showMessage(`❌ WordPress publish failed: ${data.message}`, 'error');
        }
    } catch (err) {
        showMessage('❌ WordPress publish error', 'error');
        console.error(err);
    }
}

let messageTimeout;
function showMessage(text, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = type;
    messageEl.style.display = 'block';
    
    if (messageTimeout) clearTimeout(messageTimeout);
    if (type !== 'error') {
        messageTimeout = setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }
}
