"""The reader, and the session held over it.

Nothing is imported here on purpose. The modules under this package reach the
CLR, numpy and the private runtime folder, none of which exist until a driver has
said where its workspace is and the bring-up has run (:mod:`Kernel.bootstrap`) --
so importing this package must cost nothing at all. Consumers import the module
they want by name, after that.

    ``pythonnet_bridge``  claims the runtime and wraps the reader's own surface
    ``cabmap_state``      the open session: which install, which map, what is picked
    ``column_table``      a published table, over the buffers it was built from
    ``bootstrap``         the private dependency folder
    ``workspace``         where this application keeps its own files
    ``reader_settings``   what the user told the reader, per install
    ``session``           asking the open session for a published dataset
"""
