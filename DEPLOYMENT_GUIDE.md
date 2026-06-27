# Deploy Retail Credit Intelligence Dashboard to Streamlit Cloud

## Step 1: Make GitHub Repository Public (if not already)

1. Go to your repository: https://github.com/AdirAmitaf-RidaFatima/Retail-Credit
2. Click **Settings** → scroll to **Danger Zone**
3. If repository is private, click **Change visibility** and select **Public**
4. Confirm the change

## Step 2: Deploy to Streamlit Cloud

### Option A: Direct Deployment (Recommended)

1. Go to https://share.streamlit.io
2. Click **"Create app"** button
3. Sign in with your GitHub account (if not already signed in)
4. Fill in the deployment form:
   - **Repository**: `AdirAmitaf-RidaFatima/Retail-Credit`
   - **Branch**: `main`
   - **Main file path**: `retail_credit_intelligence_workspace/app.py`
5. Click **Deploy!**

The dashboard will start deploying and should be live in 2-3 minutes.

Your public URL will be: `https://share.streamlit.io/AdirAmitaf-RidaFatima/Retail-Credit/main/retail_credit_intelligence_workspace/app.py`

### Option B: Using Command Line

```bash
# Install Streamlit CLI if not already installed
pip install streamlit

# From the dashboard directory, run:
cd retail_credit_intelligence_workspace
streamlit run app.py --logger.level=info
```

## Step 3: Share the Link

Once deployed, share the public URL with anyone who wants to access the dashboard. No authentication required!

## Managing Deployments

- **Updates**: Any changes you push to the `main` branch will automatically redeploy
- **Logs**: View deployment logs in the Streamlit Cloud dashboard
- **Custom Domain**: Upgrade to Pro to use a custom domain
- **Performance**: Free tier includes up to 3 apps. If you need more, upgrade your account

## Troubleshooting

**Problem**: App fails to deploy
- Check that `retail_credit_intelligence_workspace/app.py` exists
- Ensure `requirements.txt` is in the same directory
- Check the deployment logs for errors

**Problem**: Data file not found
- Ensure all data files are committed to git
- The `data/` directory is included in the repository

**Problem**: App is slow
- Free tier has limited resources. Consider upgrading for better performance
- Large datasets may take time to load initially

---

**Status**: Your repository is now public and can be deployed! 🚀
