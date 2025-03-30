import os
import importlib.util
import util.database as db
from nextcord.ext import commands

async def load_cogs(bot):
    await db.init_db()
    for entry in os.listdir("cogs"):
        if entry.endswith(".py"):
            module_name = f"cogs.{entry[:-3]}"
            if _has_setup(module_name):
                _load_extension(bot, module_name)
        elif os.path.isdir(f"cogs/{entry}"):
            for filename in os.listdir(f"cogs/{entry}"):
                if filename.endswith(".py"):
                    module_name = f"cogs.{entry}.{filename[:-3]}"
                    if _has_setup(module_name):
                        _load_extension(bot, module_name)

def _has_setup(module_name):
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        return False
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return hasattr(module, "setup")

def _load_extension(bot, module_name):
    try:
        bot.load_extension(module_name)
    except Exception as e:
        print(f"Failed to load {module_name}: {e}")

async def reload_cog(bot, cog_name):
    try:
        bot.unload_extension(f"cogs.{cog_name}")
        bot.load_extension(f"cogs.{cog_name}")
        return f"Reloaded `{cog_name}` successfully."
    except commands.ExtensionNotLoaded:
        return f"Cog `{cog_name}` is not loaded."
    except commands.ExtensionNotFound:
        return f"Cog `{cog_name}` not found."
    except Exception as e:
        return f"Error reloading `{cog_name}`: {e}"

async def unload_cog(bot, cog_name):
    try:
        bot.unload_extension(f"cogs.{cog_name}")
        return f"Unloaded `{cog_name}` successfully."
    except commands.ExtensionNotLoaded:
        return f"Cog `{cog_name}` is not loaded."
    except commands.ExtensionNotFound:
        return f"Cog `{cog_name}` not found."
    except Exception as e:
        return f"Error unloading `{cog_name}`: {e}"

async def load_cog(bot, cog_name):
    try:
        bot.load_extension(f"cogs.{cog_name}")
        return f"Loaded `{cog_name}` successfully."
    except commands.ExtensionAlreadyLoaded:
        return f"Cog `{cog_name}` is already loaded."
    except commands.ExtensionNotFound:
        return f"Cog `{cog_name}` not found."
    except Exception as e:
        return f"Error loading `{cog_name}`: {e}"
