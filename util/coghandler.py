import os
import importlib.util

def load_cogs(bot):
    for entry in os.listdir("cogs"):
        if entry.endswith(".py"):
            module_name = f"cogs.{entry[:-3]}"
            if _has_setup(module_name):
                bot.load_extension(module_name)
        elif os.path.isdir(f"cogs/{entry}"):
            for filename in os.listdir(f"cogs/{entry}"):
                if filename.endswith(".py"):
                    module_name = f"cogs.{entry}.{filename[:-3]}"
                    if _has_setup(module_name):
                        bot.load_extension(module_name)

def _has_setup(module_name):
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        return False
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return hasattr(module, "setup")