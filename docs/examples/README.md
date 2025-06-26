# 💡 Examples

Real-world implementation examples for the MCP Server Template, demonstrating various use cases and integration patterns.

## 📁 Example Collection

### Basic Examples
- **[Simple Calculator](basic-calculator.md)** - Basic arithmetic operations
- **[Text Processing](text-processing.md)** - String manipulation and analysis
- **[File Operations](file-operations.md)** - File reading, writing, and management

### Intermediate Examples
- **[Database Integration](database-integration.md)** - Database operations with SQLAlchemy
- **[API Integration](api-integration.md)** - External API calls and data fetching
- **[Background Tasks](background-tasks.md)** - Async task processing and job queues

### Advanced Examples
- **[Multi-model AI](multi-model-ai.md)** - Integration with multiple AI services
- **[Microservices](microservices.md)** - MCP server as part of microservices architecture
- **[Production Deployment](production-deployment.md)** - Complete production setup

### Integration Examples
- **[Cursor IDE Integration](cursor-integration.md)** - Setup and usage with Cursor
- **[Claude Desktop](claude-desktop.md)** - Integration with Claude Desktop
- **[Custom Client](custom-client.md)** - Building custom MCP clients

## 🚀 Quick Start with Examples

### Running Examples

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd mcp-server-template
   ```

2. **Install dependencies**:
   ```bash
   uv sync --extra dev
   ```

3. **Run an example**:
   ```bash
   # Copy example configuration
   cp docs/examples/basic-calculator/tools.py src/tools/calculator_tools.py
   
   # Update tool loading
   # Edit src/tools/__init__.py to include "tools.calculator_tools"
   
   # Run the server
   python src/server.py
   ```

4. **Test the example**:
   ```bash
   python docs/examples/basic-calculator/test_calculator.py
   ```

## 📋 Example Structure

Each example includes:

- **README.md** - Detailed explanation and setup instructions
- **Implementation files** - Complete working code
- **Test files** - Example usage and tests
- **Configuration** - Environment and settings
- **Documentation** - API reference and usage guide

## 🛠️ Creating Your Own Examples

### Example Template

```
my-example/
├── README.md              # Description and setup
├── tools.py              # Tool implementations
├── resources.py          # Resource implementations (optional)
├── prompts.py            # Prompt implementations (optional)
├── test_example.py       # Test and usage examples
├── requirements.txt      # Additional dependencies (optional)
└── .env.example         # Environment variables
```

### Guidelines

1. **Clear Documentation** - Explain what the example does and how to use it
2. **Complete Code** - Provide fully working implementations
3. **Error Handling** - Include proper error handling and validation
4. **Testing** - Provide test cases and usage examples
5. **Real-world Focus** - Solve actual problems that developers face

## 🔍 Finding Examples

### By Use Case

- **Data Processing**: text-processing, database-integration
- **External APIs**: api-integration, multi-model-ai
- **File Management**: file-operations
- **Development Tools**: cursor-integration, claude-desktop
- **Deployment**: production-deployment, microservices

### By Complexity

- **Beginner**: basic-calculator, text-processing
- **Intermediate**: database-integration, api-integration
- **Advanced**: multi-model-ai, microservices, production-deployment

### By Technology

- **Database**: database-integration (SQLAlchemy, PostgreSQL)
- **AI/ML**: multi-model-ai (OpenAI, Anthropic, local models)
- **Web APIs**: api-integration (httpx, requests)
- **Containers**: production-deployment (Docker, Kubernetes)

## 🤝 Contributing Examples

We welcome contributions! To add a new example:

1. **Create a new directory** in `docs/examples/`
2. **Follow the example template** structure
3. **Test your example** thoroughly
4. **Submit a pull request** with clear documentation

### Example Contribution Checklist

- [ ] Clear, descriptive README
- [ ] Complete working code
- [ ] Proper error handling
- [ ] Test cases included
- [ ] Environment setup documented
- [ ] No hardcoded secrets or credentials
- [ ] Follows project coding standards

## 📚 Additional Resources

- **[Quick Start Guide](../quickstart.md)** - Get started with the template
- **[Development Guide](../development.md)** - Advanced development patterns
- **[API Reference](../api-reference.md)** - Complete API documentation
- **[Deployment Guide](../deployment.md)** - Production deployment

## 🆘 Getting Help

If you have questions about the examples:

1. **Check the example README** - Most common issues are covered
2. **Review the main documentation** - Especially the development guide
3. **Open an issue** - For bugs or missing information
4. **Start a discussion** - For general questions and ideas

---

**Happy coding!** These examples are designed to help you build amazing MCP servers quickly and efficiently. 