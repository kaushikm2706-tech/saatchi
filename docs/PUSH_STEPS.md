# Put the repo on GitHub (exact steps)
1. Go to github.com, click "+" (top right) > "New repository". Name: saatchi. Choose PUBLIC (rules require it). Do NOT tick README/.gitignore/license. Click "Create repository".
2. Unpack the tar file into a folder. Open PowerShell in the saatchi folder.
3. Check your identity: `git log --format="%an <%ae>"`. It must show `Kaushik M <296336871+kaushikm2706-tech@users.noreply.github.com>`.
4. `git remote add origin https://github.com/kaushikm2706-tech/saatchi.git`
5. `git branch -M main` then `git push -u origin main` (sign in when the browser asks).
6. Open the repo page logged out (private window) to confirm it is public.
