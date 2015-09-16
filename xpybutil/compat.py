try:
    import xcffib as xcb
    import xcffib.xproto as xproto
    import xcffib.xinerama as xinerama
    import xcffib.randr as randr
    import xcffib.render as render
    from xcffib import XcffibException as xcb_Exception
    from xcffib import ConnectionException as xcb_ConnectException

except ImportError:
    import xcb
    import xcb.xproto as xproto
    import xcb.xinerama as xinerama
    import xcb.randr as randr
    import xcb.render as render
    from xcb import Exception as xcb_Exception
    from xcb import ConnectException as xcb_ConnectException
