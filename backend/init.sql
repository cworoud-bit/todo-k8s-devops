-- Create tasks table if it doesn't exist
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO tasks (title, description, status) VALUES
    ('Apprendre Docker', 'Compléter le laboratoire Docker Compose', 'in_progress'),
    ('Configurer les réseaux', 'Implémenter la segmentation réseau', 'pending'),
    ('Tester les volumes', 'Vérifier la persistance des données', 'pending'),
    ('Documenter le projet', 'Rédiger le README et prendre les captures', 'completed')
ON CONFLICT (id) DO NOTHING;