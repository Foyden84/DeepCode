# ICRA User Guide

## Interactive Code Review Agent - Complete User Guide

### Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Creating Reviews](#creating-reviews)
4. [Reviewing Code](#reviewing-code)
5. [Security Analysis](#security-analysis)
6. [Collaboration Features](#collaboration-features)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- DeepCode system installed and configured
- Python 3.8+ environment
- Access to the ICRA dashboard

### Accessing ICRA
1. Launch the DeepCode application
2. In the sidebar, look for the "🔍 Code Review" section
3. Click "🚀 Launch ICRA Dashboard"
4. The ICRA interface will load in the main area

### First Time Setup
1. Ensure your Git repositories are accessible
2. Configure any necessary API keys for external integrations
3. Review the default security policies in the settings

## Dashboard Overview

### Main Components

#### Review Overview Panel
- **Active Reviews**: Number of currently active reviews
- **Completed Today**: Reviews completed in the last 24 hours
- **Security Issues Found**: Total security vulnerabilities detected
- **Avg Review Time**: Average time to complete reviews

#### Active Reviews Table
Displays all current reviews with:
- Review ID and title
- Author information
- Current status (Pending, In Review, Approved, Rejected)
- Priority level
- Files changed count
- Security score

#### Code Diff Viewer
- Side-by-side comparison of original and modified code
- Syntax highlighting for multiple programming languages
- Line-by-line analysis with AI suggestions
- Interactive commenting on specific lines

#### Collaboration Panel
- Real-time user presence indicators
- Live comments and discussions
- Notification system
- Chat functionality

#### Security Analysis Panel
- Overall security score
- Detailed vulnerability findings
- Risk assessment
- Remediation recommendations

## Creating Reviews

### Manual Review Creation
1. Click "Create New Review" button
2. Fill in the review details:
   - Repository URL
   - Pull Request/Branch information
   - Reviewer assignments
   - Priority level
3. Click "Start Review" to initiate the process

### Automatic Review Triggers
ICRA can automatically create reviews when:
- New pull requests are opened
- Code is pushed to monitored branches
- Security thresholds are exceeded

### Review Configuration
- Set custom security policies
- Configure notification preferences
- Define reviewer assignment rules
- Set up integration with CI/CD pipelines

## Reviewing Code

### Step-by-Step Review Process

#### 1. Select a Review
- Choose a review from the Active Reviews table
- Click on the review ID to load details

#### 2. Examine Code Changes
- Use the file selector to navigate between changed files
- Review the side-by-side diff view
- Pay attention to AI-generated suggestions and warnings

#### 3. Security Analysis
- Check the security score in the right panel
- Review any detected vulnerabilities
- Read the remediation recommendations

#### 4. Add Comments
- Click on specific lines to add inline comments
- Use the comment panel for general feedback
- Tag other reviewers using @mentions

#### 5. Make Decision
- **Approve**: Click the green "✅ Approve" button
- **Request Changes**: Click "❌ Request Changes" and provide feedback
- **Add Comments**: Use "💬 Add Comment" for questions or suggestions

### Best Practices
- Review security findings first
- Check for proper error handling
- Verify input validation
- Ensure code follows team standards
- Test critical functionality changes

## Security Analysis

### Understanding Security Scores
- **90-100**: Excellent security posture
- **70-89**: Good with minor issues
- **50-69**: Moderate risk, needs attention
- **Below 50**: High risk, requires immediate action

### Vulnerability Types
ICRA detects various security issues:

#### Critical Issues
- Hardcoded secrets and passwords
- SQL injection vulnerabilities
- Command injection risks
- Path traversal vulnerabilities

#### High Priority Issues
- Cross-site scripting (XSS)
- Authentication bypasses
- Insecure file uploads
- Missing access controls

#### Medium Priority Issues
- Weak cryptographic algorithms
- Missing security headers
- Session management issues
- Input validation gaps

#### Low Priority Issues
- Information disclosure
- Deprecated functions
- Code quality concerns

### Custom Security Policies
1. Access the Security Settings panel
2. Review existing policies
3. Enable/disable specific rules
4. Configure severity levels
5. Set up custom patterns for your codebase

## Collaboration Features

### Real-time Collaboration
- **Live Presence**: See who else is reviewing the code
- **Instant Comments**: Comments appear immediately for all users
- **Live Cursors**: See where other reviewers are looking
- **Notifications**: Get notified of new comments and changes

### Communication Tools
- **Inline Comments**: Comment on specific lines of code
- **General Discussion**: Use the discussion panel for broader topics
- **@Mentions**: Tag specific team members
- **Emoji Reactions**: Quick reactions to comments

### Notification System
Configure notifications for:
- New reviews assigned to you
- Comments on your reviews
- Security issues detected
- Review status changes

## Advanced Features

### Integration with External Tools

#### Git Integration
- Automatic pull request monitoring
- Branch protection rules
- Commit status updates
- Merge conflict detection

#### CI/CD Integration
- Trigger reviews on build completion
- Block deployments on security issues
- Generate review reports
- Update ticket systems

#### Slack/Teams Integration
- Review notifications in chat
- Status updates
- Quick approval workflows
- Team mentions

### API Usage
For programmatic access:
```bash
# Create a review
curl -X POST http://localhost:8000/reviews \
  -H "Content-Type: application/json" \
  -d '{"repository_url": "https://github.com/user/repo", "pull_request_id": "123"}'

# Get review status
curl http://localhost:8000/reviews/{review_id}

# Add comment
curl -X POST http://localhost:8000/reviews/{review_id}/comments \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "text": "Looks good\!"}'
```

### Bulk Operations
- Review multiple pull requests simultaneously
- Batch approve low-risk changes
- Mass comment on similar issues
- Export review data for analysis

## Troubleshooting

### Common Issues

#### ICRA Dashboard Not Loading
1. Check that all ICRA components are installed
2. Verify the DeepCode system is running
3. Check browser console for JavaScript errors
4. Try refreshing the page

#### Reviews Not Processing
1. Verify repository access permissions
2. Check API connectivity
3. Review system logs for errors
4. Ensure sufficient system resources

#### Security Analysis Missing
1. Confirm security engine is running
2. Check security policy configuration
3. Verify file types are supported
4. Review security agent logs

#### Collaboration Features Not Working
1. Check WebSocket connectivity
2. Verify user permissions
3. Clear browser cache
4. Check firewall settings

### Performance Optimization
- Limit concurrent reviews for better performance
- Use file filters to focus on important changes
- Configure appropriate timeout settings
- Monitor system resource usage

### Getting Help
- Check the system logs for detailed error messages
- Review the API documentation for integration issues
- Contact your system administrator for configuration problems
- Submit bug reports with detailed reproduction steps

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter`: Approve review
- `Ctrl/Cmd + R`: Refresh review data
- `Ctrl/Cmd + /`: Add comment
- `Esc`: Close current dialog
- `Tab`: Navigate between UI elements
- `Space`: Toggle file selection

## Tips and Best Practices

### For Reviewers
1. Start with security analysis
2. Focus on critical and high-priority issues first
3. Provide constructive feedback
4. Use inline comments for specific issues
5. Approve quickly when appropriate

### For Authors
1. Address security issues immediately
2. Respond to comments promptly
3. Update code based on feedback
4. Test changes thoroughly
5. Keep pull requests focused and small

### For Teams
1. Establish clear review guidelines
2. Set up appropriate notification rules
3. Use consistent security policies
4. Regular team training on security best practices
5. Monitor review metrics for continuous improvement

---

For additional support or feature requests, please contact your system administrator or refer to the technical documentation.
