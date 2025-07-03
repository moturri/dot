return {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = { "williamboman/mason.nvim" },
    opts = {
        ensure_installed = {
            -- formatters
            "stylua",
            "isort",
            "black",
            "prettier",
            "clang-format",
            "shfmt",

            -- linters
            "codespell",
            "shellcheck",
        },
    },
}