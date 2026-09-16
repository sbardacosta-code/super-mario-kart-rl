"""RSS sampling with an explicit fallback when child enumeration is blocked."""
import psutil

def sample_rss(process):
    parent=process.memory_info().rss
    try:
        return parent+sum(c.memory_info().rss for c in process.children(recursive=True)), 'parent_and_children', None
    except (psutil.Error,PermissionError) as exc:
        return parent, 'parent_only', type(exc).__name__+': '+str(exc)
