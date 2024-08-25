.PHONY: clean 
clean: 
	rm -rfv _build
	rm -rfv __pycache__
	rm -rfv .pytest_cache

.PHONY: rm-elixir-ls
rm-elixir-ls:
	rm -rfv .elixir_ls
