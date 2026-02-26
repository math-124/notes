# Example Jupyter Book

This folder contains a minimal Jupyter Book example. There's no need to follow these instructions for now (and as we get to actually writing I will tweak them slightly), but I've left them here to give you a sense of what steps are necessary. Run the commands `here` in your Terminal.

1. Create and activate a virtual environment. This is a good idea, but not strictly necessary. (It ensures that you're using the same versions of packages as me, and prevents conflicts with other projects you may be working on.)

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies. This will install the packages listed in `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

3. Start a local copy of the book site in your browser.

   ```bash
   jupyter book start
   ```

4. Open the files in `01_vectors`, `02_linear_maps`, etc. in either VS Code or in Jupyter Notebooks directly and edit them. If you're just viewing this on github.com, you can see what they look like on the web. If you don't have VS Code installed, install it from [here](https://code.visualstudio.com/).