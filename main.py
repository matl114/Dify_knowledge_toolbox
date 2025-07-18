from dify_plugin import Plugin, DifyPluginEnv

env = DifyPluginEnv(MAX_REQUEST_TIMEOUT=120)

plugin = Plugin(env)

if __name__ == '__main__':
    plugin.run()
