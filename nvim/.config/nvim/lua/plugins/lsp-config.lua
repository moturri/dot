return {
  -- Mason Setup
  {
    "williamboman/mason.nvim",
    version = "*",
    lazy = true,
    event = "BufRead", -- Lazy load on BufRead
    config = function()
      require("mason").setup({
        ui = {
          border = "rounded",          -- Optional border styling for Mason UI
        },
        automatic_installation = true, -- Automatically install missing servers
      })

      -- Ensure fidget is installed properly
      local fidget_ok, fidget = pcall(require, "fidget")
      if fidget_ok then
        fidget.setup({})
      else
        vim.notify("Fidget plugin not found. Some features may be missing.")
      end
    end,
  },

  -- Mason-LSPConfig Setup
  {
    "williamboman/mason-lspconfig.nvim",
    version = "*",
    lazy = true,
    event = "BufRead", -- Lazy load on BufRead
    opts = {
      automatic_installation = true,
    },
  },

  -- LSPConfig Setup
  {
    "neovim/nvim-lspconfig",
    version = "*",
    lazy = true,
    event = "BufRead", -- Lazy load on BufRead
    config = function()
      local lspconfig = require("lspconfig")
      local mason_lspconfig = require("mason-lspconfig")

      -- Capabilities (with fallback if cmp_nvim_lsp is missing)
      local has_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
      local capabilities = has_cmp and cmp_nvim_lsp.default_capabilities()
          or vim.lsp.protocol.make_client_capabilities()

      -- Keybindings + navic attach
      local function on_attach(client, bufnr)
        local opts = { noremap = true, silent = true, buffer = bufnr }
        local keymap = vim.keymap.set

        keymap("n", "K", vim.lsp.buf.hover, opts)
        keymap("n", "<leader>gd", vim.lsp.buf.definition, opts)
        keymap("n", "<leader>gr", vim.lsp.buf.references, opts)
        keymap("n", "<leader>ca", vim.lsp.buf.code_action, opts)
        keymap("n", "<leader>rn", vim.lsp.buf.rename, opts)
        keymap("n", "<leader>f", function()
          vim.lsp.buf.format({ async = true })
        end, opts)

        -- Attach nvim-navic if available and supported
        local navic_ok, navic = pcall(require, "nvim-navic")
        if navic_ok and client.server_capabilities.documentSymbolProvider then
          navic.attach(client, bufnr)
        end
      end

      -- Diagnostic config (no deprecated sign_define)
      vim.diagnostic.config({
        virtual_text = true,
        signs = {
          text = {
            [vim.diagnostic.severity.ERROR] = "",
            [vim.diagnostic.severity.WARN] = "",
            [vim.diagnostic.severity.HINT] = "",
            [vim.diagnostic.severity.INFO] = "",
          },
        },
        underline = true,
        update_in_insert = false,
        severity_sort = true,
      })

      -- Base config shared across servers
      local default_config = {
        on_attach = on_attach,
        capabilities = capabilities,
      }

      -- Setup LSP servers individually via mason-lspconfig
      local servers = mason_lspconfig.get_installed_servers()
      for _, server_name in ipairs(servers) do
        lspconfig[server_name].setup(default_config)
      end
    end,
  },
}
