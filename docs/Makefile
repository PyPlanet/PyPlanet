# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = PyPlanet
SOURCEDIR     = source
BUILDDIR      = build

GH_DIR        = build/html

GH_REPO_URL   = git@github.com:PyPlanet/PyPlanet.git
GH_BRANCH     = gh-pages

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile


.PHONY: gh-init
gh-init:
	@echo
	@echo "Init github pages deployment..."
	@mkdir -p $(GH_DIR)
	@cd $(GH_DIR); git init; \
		git checkout -b $(GH_BRANCH);\
		git remote add origin $(GH_REPO_URL);
	@cd $(GH_DIR);\
		if ! git ls-remote origin $(GH_BRANCH) | grep $(GH_BRANCH) ; then \
			echo "Preparing Github deployment branch: $(GH_BRANCH) for the first time only...";\
    		git push -u origin $(GH_BRANCH);\
    	fi
	@cd $(GH_DIR);\
		git fetch origin;\
		git reset --hard origin/$(GH_BRANCH);\
		git clean -f;

.PHONY: gh-deploy
gh-deploy:
	@echo
	@echo "Build docs..."
	make html
	@echo "Commit..."
	@cd $(GH_DIR);\
		git add --all;\
		git commit -m "Update documentation...";\
		git push -u origin $(GH_BRANCH);


.PHONY: livehtml
livehtml:
	sphinx-autobuild -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -i *___jb_*___


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
