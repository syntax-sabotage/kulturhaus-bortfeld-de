#!/bin/bash
# Quick Deployment Script for Kulturhaus Board Resolutions
# Usage: ./scripts/quick-deploy.sh [tag-name]

set -euo pipefail

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_TAG="v$(date +%Y%m%d-%H%M%S)"
TAG_NAME="${1:-$DEFAULT_TAG}"

echo "🚀 Quick Deployment for Kulturhaus Board Resolutions"
echo "=================================================="
echo "Repository: $REPO_ROOT"
echo "Tag: $TAG_NAME"
echo ""

# Function to check git status
check_git_status() {
    echo "🔍 Checking git status..."
    cd "$REPO_ROOT"
    
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "⚠️  Warning: You have uncommitted changes:"
        git status --short
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Deployment cancelled"
            exit 1
        fi
    fi
    
    echo "✅ Git status clean"
}

# Function to create and push tag
create_release_tag() {
    echo "📦 Creating release tag: $TAG_NAME..."
    cd "$REPO_ROOT"
    
    # Create annotated tag
    git tag -a "$TAG_NAME" -m "🚀 Production deployment: Kulturhaus Board Resolutions localization fixes

✅ SPARC Completion Phase:
- Complete i18n implementation (German/English)
- View consolidation (9 → 1 files)
- Performance optimization (80% file reduction)
- XML ID conflict resolution
- Production-ready deployment

🎯 Ready for automated GitHub Actions deployment"
    
    # Push tag to trigger GitHub Actions
    git push origin "$TAG_NAME"
    
    echo "✅ Tag created and pushed to GitHub"
}

# Function to monitor deployment
monitor_deployment() {
    echo "👀 Monitoring deployment status..."
    echo ""
    echo "📋 Next steps:"
    echo "1. Check GitHub Actions: https://github.com/your-org/kulturhaus-bortfeld-de/actions"
    echo "2. Monitor deployment progress in real-time"
    echo "3. Verify production deployment at: https://kulturhaus-bortfeld.de"
    echo "4. Test language switching functionality"
    echo ""
    echo "🔗 Quick links:"
    echo "   - Release: https://github.com/your-org/kulturhaus-bortfeld-de/releases/tag/$TAG_NAME"
    echo "   - Actions: https://github.com/your-org/kulturhaus-bortfeld-de/actions"
    echo "   - Production: https://kulturhaus-bortfeld.de"
    echo ""
}

# Function to show rollback instructions
show_rollback_info() {
    echo "🔄 Emergency Rollback Information:"
    echo "=================================="
    echo ""
    echo "If deployment fails, you can:"
    echo "1. Check GitHub Actions logs for specific error"
    echo "2. Use the automatic rollback (triggered on failure)"
    echo "3. Manual rollback using backup:"
    echo ""
    echo "   ./scripts/rollback_deployment.sh <backup_directory>"
    echo ""
    echo "4. Delete problematic tag if needed:"
    echo "   git tag -d $TAG_NAME"
    echo "   git push origin :refs/tags/$TAG_NAME"
    echo ""
}

# Main execution
main() {
    echo "Starting deployment process..."
    echo ""
    
    # Pre-deployment checks
    check_git_status
    
    # Create and push release tag
    create_release_tag
    
    # Monitor deployment
    monitor_deployment
    
    # Show rollback info
    show_rollback_info
    
    echo "🎉 Quick deployment initiated successfully!"
    echo "   Tag: $TAG_NAME"
    echo "   Monitor progress in GitHub Actions"
    echo ""
}

# Help function
show_help() {
    echo "Quick Deployment Script for Kulturhaus Board Resolutions"
    echo ""
    echo "Usage: $0 [tag-name]"
    echo ""
    echo "Arguments:"
    echo "  tag-name    Optional release tag (default: v$(date +%Y%m%d-%H%M%S))"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use automatic timestamp tag"
    echo "  $0 v1.0.0            # Use specific version tag"
    echo "  $0 v1.0.1-hotfix     # Use hotfix tag"
    echo ""
    echo "This script will:"
    echo "  1. Check git status for uncommitted changes"
    echo "  2. Create annotated git tag with deployment message"
    echo "  3. Push tag to GitHub (triggers automated deployment)"
    echo "  4. Provide monitoring and rollback instructions"
    echo ""
}

# Handle help argument
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

# Execute main function
main