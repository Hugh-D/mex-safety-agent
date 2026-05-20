const { getDefaultConfig } = require("expo/metro-config")
const path = require("path")

const projectRoot = __dirname
const workspaceRoot = path.resolve(projectRoot, "../..")

const config = getDefaultConfig(projectRoot)

// Must include workspace root so Metro can serve hoisted node_modules (react-native etc)
config.watchFolders = [workspaceRoot]

// Resolve packages: mobile-local first, then workspace root (for hoisted deps)
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, "node_modules"),
  path.resolve(workspaceRoot, "node_modules"),
]

// Block Metro from watching api/ and apps/web to reduce file scan overhead
config.resolver.blockList = [
  /mex-safety-platform[/\\]api[/\\].*/,
  /mex-safety-platform[/\\]apps[/\\]web[/\\].*/,
]

module.exports = config
