Final project/
├── frontend/
│   ├── app.py                      # Streamlit main application
│   └── assets/                     # Static assets for Streamlit
│       └── template-previews/      # Template preview images
│           ├── minimal.jpg
│           ├── creative.jpg
│           └── professional.jpg
├── backend/
│   ├── api.py                      # FastAPI for backend API
│   ├── utils/
│   │   ├── __init__.py             # Make utils a package
│   │   ├── resume_processor.py     # Resume processing with Gemini
│   │   ├── portfolio_generator.py  # Portfolio generation with Gemini
│   │   └── github_integration.py   # GitHub API integration
│   ├── config.py                   # Configuration and template definitions
│   ├── uploads/                    # Directory for user resume data
│   └── results/                    # Directory for generation results
├── .env                            # Environment variables
└── requirements.txt                # Python dependencies