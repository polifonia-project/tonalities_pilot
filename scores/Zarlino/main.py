import verovio

tk = verovio.toolkit()
tk.loadFile("Zarlino_Ave_Maria.mei")
print(tk.getPageWithElement("n1670toe"))
