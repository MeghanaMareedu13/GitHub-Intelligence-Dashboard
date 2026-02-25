import streamlit as st
import pandas as pd
import plotly.express as px
from api_client import GitHubClient
from processor import GitHubDataProcessor
import logging

# App Config
st.set_page_config(page_title="GitHub Intelligence Dashboard", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("📊 GitHub Intelligence Dashboard")
st.markdown("---")

# Sidebar for Setup
st.sidebar.header("Settings")
username = st.sidebar.text_input("Enter GitHub Username", value="MeghanaMareedu13")
api_token = st.sidebar.text_input("Personal Access Token (Recommended)", type="password", help="Providing a token allows up to 5000 req/hr vs 60.")

# Initialize Client
client = GitHubClient(token=api_token if api_token else None)
processor = GitHubDataProcessor()

if st.button("Fetch Intelligence Report"):
    try:
        with st.spinner(f"Analyzing {username}'s digital footprint..."):
            # 1. Fetch Basic Info
            user_info = client.get_user_info(username)
            
            # 2. Fetch Repos
            repos = client.get_user_repos(username)
            
            if not repos:
                st.warning("No public repositories found for this user.")
            else:
                # Layout
                col1, col2, col3 = st.columns(3)
                col1.metric("Followers", user_info.get('followers', 0))
                col2.metric("Public Repos", user_info.get('public_repos', 0))
                col3.metric("Public Gists", user_info.get('public_gists', 0))

                # Process Analytics
                repo_df = processor.process_repo_metrics(repos)
                
                # Language Analysis (Sampling top 5 repos to save rate limits if no token)
                st.subheader("🛠️ Technical Breadth (Language Distribution)")
                lang_data_list = []
                # limit to 10 repos for performance/rate limits
                for repo in repos[:10]:
                    langs = client.get_repo_languages(username, repo['name'])
                    lang_data_list.append(langs)
                
                lang_df = processor.process_languages(lang_data_list)
                
                c1, c2 = st.columns(2)
                
                with c1:
                    fig_pie = px.pie(lang_df, values='Bytes', names='Language', 
                                    title="Language Composition (Top 10 Repos)",
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with c2:
                    st.markdown("### Top Project Health Scores")
                    st.dataframe(repo_df[['Name', 'Health Score', 'Primary Language']].sort_values(by='Health Score', ascending=False), 
                                 use_container_width=True, hide_index=True)

                st.markdown("---")
                
                # Detailed Repo Metrics
                st.subheader("📈 Deep Dive: Repository Performance")
                fig_scatter = px.scatter(repo_df, x="Stars", y="Health Score", size="Forks", 
                                        hover_name="Name", text="Name",
                                        title="Project Maturity vs. Popularity",
                                        color="Primary Language")
                st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"Critical Failure: {str(e)}")
        st.info("Tip: If you're seeing a 403 error, GitHub's rate limit has been reached. Please provide a Personal Access Token in the sidebar.")

# Footer
st.markdown("---")
st.caption("Day 13 | API Integration Project | Build by Meghana Mareedu")
