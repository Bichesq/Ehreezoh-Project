# Contributing to Cameroon Traffic App

Thank you for your interest in contributing to the Cameroon Traffic App! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors
- Report any unacceptable behavior to the project maintainers

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/[username]/cameroon-traffic-app/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, device, app version)

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/[username]/cameroon-traffic-app.git
   cd cameroon-traffic-app
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards (see below)
   - Write clear commit messages
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend && pytest tests/
   
   # Mobile tests
   cd mobile && npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Wait for review

## Coding Standards

### Backend (Python/FastAPI)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Use Black for formatting
- Use Flake8 for linting
- Maximum line length: 100 characters

```python
# Good example
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in meters
    """
    # Implementation here
    pass
```

### Mobile (React Native/TypeScript)

- Follow Airbnb JavaScript Style Guide
- Use TypeScript for type safety
- Use functional components with hooks
- Use ESLint for linting
- Use Prettier for formatting
- Maximum line length: 100 characters

```typescript
// Good example
interface IncidentMarkerProps {
  incident: Incident;
  onPress: (id: string) => void;
}

const IncidentMarker: React.FC<IncidentMarkerProps> = ({ incident, onPress }) => {
  const handlePress = useCallback(() => {
    onPress(incident.id);
  }, [incident.id, onPress]);

  return (
    <Marker coordinate={incident.location} onPress={handlePress}>
      {/* Marker content */}
    </Marker>
  );
};
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(incidents): add photo upload functionality
fix(map): resolve marker clustering issue
docs(api): update endpoint documentation
test(auth): add unit tests for login flow
```

## Development Workflow

1. **Week 1-2:** Setup & Planning
2. **Week 3-4:** Backend Foundation
3. **Week 5-6:** Mobile App Core
4. **Week 7-8:** Reporting Features
5. **Week 9-10:** Real-time Features
6. **Week 11-12:** Testing & Launch

See [PROGRESS.md](PROGRESS.md) for detailed task breakdown.

## Testing Guidelines

### Backend Tests
- Write unit tests for all business logic
- Write integration tests for API endpoints
- Aim for >70% code coverage
- Use pytest fixtures for test data

### Mobile Tests
- Write unit tests for utilities and services
- Write component tests for UI components
- Write integration tests for user flows
- Use Jest and React Testing Library

## Documentation

- Update README.md for major changes
- Update API documentation for endpoint changes
- Add inline comments for complex logic
- Update PROJECT_DOCUMENTATION.md for architectural changes

## Questions?

If you have questions about contributing:
- Check existing documentation
- Search closed issues
- Create a new issue with the "question" label
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make Cameroon roads safer! 🚗🇨🇲

