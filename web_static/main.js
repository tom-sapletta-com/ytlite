let currentView = 'grid';

function toggleView() {
    currentView = currentView === 'grid' ? 'table' : 'grid';
    const projectsList = document.getElementById('projects-list');
    projectsList.className = currentView === 'grid' ? 'grid-view' : 'table-view';
    updateProjectsList();
}

function updateProjectsList() {
    fetch('/api/projects')
        .then(response => response.json())
        .then(projects => {
            const projectsList = document.getElementById('projects-list');
            projectsList.innerHTML = '';
            if (currentView === 'grid') {
                projects.forEach(project => {
                    const projectCard = document.createElement('div');
                    projectCard.className = 'project-card';
                    projectCard.innerHTML = `
                        <h2>${project.name}</h2>
                        <img src="/api/thumbnail/${project.id}" alt="${project.name} Thumbnail" style="max-width: 100px; max-height: 100px;">
                        <p>${project.description}</p>
                    `;
                    projectCard.onclick = () => showProjectPreview(project.id);
                    projectsList.appendChild(projectCard);
                });
            } else {
                const table = document.createElement('table');
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Thumbnail</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                `;
                const tbody = table.querySelector('tbody');
                projects.forEach(project => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${project.name}</td>
                        <td>${project.description}</td>
                        <td><img src="/api/thumbnail/${project.id}" alt="${project.name} Thumbnail" style="max-width: 50px; max-height: 50px;"></td>
                    `;
                    row.onclick = () => showProjectPreview(project.id);
                    tbody.appendChild(row);
                });
                projectsList.appendChild(table);
            }
        })
        .catch(error => console.error('Error fetching projects:', error));
}

function showProjectPreview(projectId) {
    fetch(`/api/project/${projectId}`)
        .then(response => response.json())
        .then(project => {
            const preview = document.getElementById('project-preview');
            preview.innerHTML = `
                <h2>${project.name}</h2>
                <p>${project.description}</p>
                <img src="/api/thumbnail/${project.id}" alt="${project.name} Thumbnail" style="max-width: 200px; max-height: 200px;">
            `;
        })
        .catch(error => console.error('Error fetching project details:', error));
}

function generateProject() {
    fetch('/api/generate', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Project generated:', data);
            updateProjectsList();
        })
        .catch(error => console.error('Error generating project:', error));
}

// Initial load
updateProjectsList();
