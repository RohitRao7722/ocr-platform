# Contributing to OCR Platform

First off, thank you for considering contributing to OCR Platform! It's people like you that make this project better.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [your.email@example.com].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Upload file '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
 - Browser: [e.g. Chrome 120, Firefox 121]
 - Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some examples** of how it would be used

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** and ensure they follow our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if you've added/changed functionality
5. **Write a clear commit message**

## Development Process

### Setting Up Your Development Environment

1. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/ocr-platform.git
   cd ocr-platform
   ```

2. **Install dependencies**
   ```bash
   # Backend
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env as needed
   ```

4. **Start development servers**
   ```bash
   # Backend (from backend directory)
   uvicorn app.main:app --reload
   
   # Frontend (from frontend directory)
   npm run dev
   ```

### Coding Standards

#### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 100 characters
- Use meaningful variable and function names

**Example:**
```python
def process_document(file_path: str, engine: str = "auto") -> Dict[str, Any]:
    """
    Process a document and extract text using OCR.
    
    Args:
        file_path: Absolute path to the document file
        engine: OCR engine to use ('auto', 'paddleocr', 'tesseract')
    
    Returns:
        Dictionary containing extracted text and metadata
    
    Raises:
        FileNotFoundError: If file_path does not exist
        ValueError: If engine is not supported
    """
    # Implementation
```

#### JavaScript/React (Frontend)

- Use ES6+ syntax
- Follow Airbnb style guide
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names

**Example:**
```javascript
/**
 * Upload form component for file selection and submission
 * @param {Function} onUpload - Callback when files are uploaded
 * @param {boolean} loading - Whether upload is in progress
 */
const UploadForm = ({ onUpload, loading }) => {
  // Implementation
};
```

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

**Good commit messages:**
```
Add batch upload support for ZIP files

- Implement ZIP extraction in batch.py
- Add frontend UI for ZIP upload
- Update API documentation
- Closes #123
```

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions
- Update API documentation for new endpoints
- Add comments for complex logic

## Project Structure

```
ocr-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── workers/      # Background tasks
│   ├── alembic/          # Database migrations
│   └── tests/            # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── utils/        # Utility functions
│   │   └── App.jsx       # Main component
│   └── public/           # Static assets
└── docs/                 # Documentation
```

## Release Process

1. Update version in `backend/app/core/config.py` and `frontend/package.json`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release with version number

## Questions?

Feel free to open an issue with the "question" label if you have any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
