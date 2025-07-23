# Vercel Deployment Instructions

Last updated: 2025-01-23

## Deployment Status
- Repository: https://github.com/sennaoyuki/ClinicStore_Scraping
- Vercel project should auto-deploy from main branch

## Environment Notes
- Uses `/tmp` directory for temporary file storage
- Maximum execution time: 60 seconds
- Python version: 3.9

## Troubleshooting
If Vercel doesn't auto-deploy:
1. Go to Vercel dashboard
2. Check deployment logs
3. Manually trigger redeploy if needed

## Recent Changes
- Fixed serverless function configuration
- Updated Flask version for compatibility
- Added proper routing for static files