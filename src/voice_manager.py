"""
Module for managing multiple voices for audio generation in ytlite.
Provides a selection of voices that can be chosen via the web GUI.
"""

class VoiceManager:
    def __init__(self):
        self.voices = {
            'pl-PL-MarekNeural': {'language': 'Polish', 'gender': 'Male', 'description': 'Marek - Natural Polish voice'},
            'pl-PL-ZofiaNeural': {'language': 'Polish', 'gender': 'Female', 'description': 'Zofia - Natural Polish voice'},
            'en-US-JennyNeural': {'language': 'English (US)', 'gender': 'Female', 'description': 'Jenny - Natural US English voice'},
            'en-US-BrianNeural': {'language': 'English (US)', 'gender': 'Male', 'description': 'Brian - Natural US English voice'},
            'de-DE-KatjaNeural': {'language': 'German', 'gender': 'Female', 'description': 'Katja - Natural German voice'},
            'de-DE-ConradNeural': {'language': 'German', 'gender': 'Male', 'description': 'Conrad - Natural German voice'},
            # Add more voices as needed
        }
        self.selected_voice = 'pl-PL-MarekNeural'  # Default voice

    def get_voice_list(self):
        """Return the list of available voices with their details."""
        return self.voices

    def set_voice(self, voice_id):
        """Set the selected voice for audio generation."""
        if voice_id in self.voices:
            self.selected_voice = voice_id
            return True, f"Voice set to {voice_id}"
        return False, f"Voice {voice_id} not found"

    def get_selected_voice(self):
        """Get the currently selected voice."""
        return self.selected_voice

if __name__ == "__main__":
    vm = VoiceManager()
    print("Available voices:", vm.get_voice_list())
    print("Current voice:", vm.get_selected_voice())
    vm.set_voice('en-US-JennyNeural')
    print("Updated voice:", vm.get_selected_voice())
