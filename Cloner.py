"""
OmniParse - GitHub Cloner
Clones any public repo with depth=1, filters noise, safety checks.
This is what makes OmniParse not a toy - real cloning, not mock.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Set
from urllib.parse import urlparse

import git
from git.exc import GitCommandError, InvalidGitRepositoryError

# Files/folders to ignore - not useful for codebase intelligence
IGNORE_PATTERNS: Set[str] = {
    ".git", "__pycache__", "node_modules", ".next", "dist", "build",
    ".venv", "venv", ".env", ".mypy_cache", ".pytest_cache",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    ".DS_Store", "*.pyc", "*.pyo", "*.so", "*.dylib"
}

IGNORE_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".mp4", ".mov", ".avi", ".mp3", ".wav", ".zip", ".tar", ".gz",
    ".pdf", ".ttf", ".woff", ".woff2", ".eot"
}

MAX_REPO_SIZE_MB = 500  # Safety: don't clone huge repos

def is_valid_github_url(url: str) -> bool:
    """Validate GitHub URL format"""
    try:
        parsed = urlparse(url)
        if parsed.netloc != "github.com":
            return False
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            return False
        return True
    except:
        return False

def get_repo_name_from_url(url: str) -> str:
    """Extract repo name: https://github.com/vercel/next.js -> next.js"""
    try:
        return url.rstrip("/").split("/")[-1].replace(".git", "")
    except:
        return "repo"

def should_ignore_path(path: Path) -> bool:
    """Check if path should be ignored"""
    name = path.name
    # Check exact names
    if name in IGNORE_PATTERNS:
        return True
    # Check extensions
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    # Check if any parent is ignored
    for part in path.parts:
        if part in IGNORE_PATTERNS:
            return True
    return False

def clone_repo(
    github_url: str,
    target_dir: Optional[Path] = None,
    depth: int = 1
) -> Path:
    """
    Clone GitHub repo with depth=1 for speed.
    
    Args:
        github_url: https://github.com/user/repo
        target_dir: Where to clone, if None uses temp dir
        depth: Git clone depth, 1 = only latest commit (fast)
    
    Returns:
        Path to cloned repo
    
    Raises:
        ValueError: Invalid URL
        GitCommandError: Clone failed
    """
    if not is_valid_github_url(github_url):
        raise ValueError(f"Invalid GitHub URL: {github_url}. Expected https://github.com/user/repo")
    
    if target_dir is None:
        temp_base = Path(tempfile.gettempdir()) / "omniparse"
        temp_base.mkdir(exist_ok=True)
        repo_name = get_repo_name_from_url(github_url)
        target_dir = temp_base / repo_name
    
    # Clean if exists
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    print(f"[Cloner] Cloning {github_url} -> {target_dir} (depth={depth})")
    
    try:
        # Clone with depth=1 for speed - don't need full history
        repo = git.Repo.clone_from(
            github_url,
            str(target_dir),
            depth=depth,
            single_branch=True,
            # Shallow clone = 10x faster
        )
        print(f"[Cloner] Cloned successfully: {target_dir}")
        
        # Safety: check size
        size_mb = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file()) / (1024*1024)
        if size_mb > MAX_REPO_SIZE_MB:
            shutil.rmtree(target_dir)
            raise ValueError(f"Repo too large: {size_mb:.1f}MB > {MAX_REPO_SIZE_MB}MB limit")
        
        # Clean ignored files after clone
        cleaned = 0
        for path in target_dir.rglob("*"):
            if should_ignore_path(path):
                try:
                    if path.is_file():
                        path.unlink()
                        cleaned += 1
                    elif path.is_dir():
                        shutil.rmtree(path)
                        cleaned += 1
                except:
                    pass
        
        print(f"[Cloner] Cleaned {cleaned} ignored files")
        return target_dir
        
    except GitCommandError as e:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        raise GitCommandError(f"Failed to clone {github_url}: {e}")
    except Exception as e:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        raise e

def cleanup_repo(repo_path: Path):
    """Clean up cloned repo after processing"""
    if repo_path.exists() and "omniparse" in str(repo_path):
        shutil.rmtree(repo_path)
        print(f"[Cloner] Cleaned up {repo_path}")

# Test
if __name__ == "__main__":
    # Test with small repo
    test_url = "https://github.com/psf/requests"
    path = clone_repo(test_url)
    print(f"Test cloned to: {path}")
    print(f"Files: {len(list(path.rglob('*.py')))} Python files")
