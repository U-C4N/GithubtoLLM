from git import Repo
from git.exc import GitCommandError
import os

class GitHandler:
    def clone_repository(self, repo_url, target_path):
        """
        Clone a GitHub repository to the specified path
        """
        try:
            # Clone the repository
            repo = Repo.clone_from(repo_url, target_path)
            return os.path.abspath(target_path)
        except GitCommandError as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")
