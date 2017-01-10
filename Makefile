INSTALL_DIR?=$(HOME)/.config/inkscape/extensions
INSTALL_FILES?=filters.svg material_shadow.inx material_shadow.py

.DEFAULT_GOAL:=install
.PHONY: install uninstall

install:
	mkdir -p $(INSTALL_DIR)
	cp $(INSTALL_FILES) $(INSTALL_DIR)

uninstall:
	rm -f $(patsubst %,$(INSTALL_DIR)/%,$(INSTALL_FILES))
