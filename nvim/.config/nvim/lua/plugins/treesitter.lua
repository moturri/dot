return {
    {
        "nvim-treesitter/nvim-treesitter",
        build = ":TSUpdate", -- Automatically update parsers
        version = "*",
        config = function()
            require("nvim-treesitter.configs").setup({
                -- List of parsers to install (choose parsers you actively use)
                ensure_installed = {},
                sync_install = false, -- Use async install for better performance
                auto_install = true, -- Auto-install missing parsers
                ignore_install = {}, -- Parsers to ignore installing (e.g., if you don't need them)

                -- Enable highlight
                highlight = {
                    enable = true, -- Enable Tree-sitter highlighting
                    additional_vim_regex_highlighting = false, -- No fallback regex highlighting
                },

                -- Enable Tree-sitter-based indentation
                indent = {
                    enable = true, -- Use Tree-sitter indentation
                },

                -- Enable incremental selection (easy selection of syntax nodes)
                incremental_selection = {
                    enable = true,
                    keymaps = {
                        init_selection = "<C-space>", -- Start selection
                        node_incremental = "<C-space>", -- Increment selection
                        scope_incremental = "<C-s>", -- Increment to the scope
                        node_decremental = "<C-backspace>", -- Decrement selection
                    },
                },

                -- Enable autotagging (for HTML/XML tags)
                autotag = {
                    enable = true, -- Automatically close/open tags
                },

                -- Enable textobjects (select functions, classes, etc.)
                textobjects = {
                    select = {
                        enable = true,
                        lookahead = true, -- Automatically jump forward to next text object
                        keymaps = {
                            ["af"] = "@function.outer", -- Select outer function
                            ["if"] = "@function.inner", -- Select inner function
                            ["ac"] = "@class.outer", -- Select outer class
                            ["ic"] = "@class.inner", -- Select inner class
                        },
                    },
                    move = {
                        enable = true,
                        set_jumps = true, -- Keep track of jumps for selection navigation
                        keymaps = {
                            ["[f"] = { query = "@function.outer", desc = "Previous function" },
                            ["]f"] = { query = "@function.outer", desc = "Next function" },
                            ["[c"] = { query = "@class.outer", desc = "Previous class" },
                            ["]c"] = { query = "@class.outer", desc = "Next class" },
                        },
                    },
                },

                -- Context-aware comment string
                context_commentstring = {
                    enable = true, -- Enable context-aware comment string
                    enable_autocmd = false, -- Disable autocmd for context commentstring
                },

                -- Performance optimizations
                -- modules = {
                --     -- Uncomment for performance optimizations for larger files
                --     textsubjects = { enable = false },
                --     rainbow = { enable = false },
                -- },

                -- Ensure proper folding using Treesitter (for large code blocks)
                fold = {
                    enable = true,
                    custom_fold = "nvim_treesitter#foldexpr()", -- Use Treesitter for intelligent folding
                },
            })
        end,
    },
}
