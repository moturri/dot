return {
  {
    "williamboman/mason.nvim",
    version = "*",
    lazy = false,
    config = function()
      require("mason").setup()

      -- Ensure fidget is installed properly
      local fidget_ok, fidget = pcall(require, "fidget")
      if fidget_ok then
        fidget.setup({})
      end
    end,
  },

  {
    "williamboman/mason-lspconfig.nvim",
    version = "*",
    lazy = false,
    opts = {
      automatic_installation = true,
    },
  },

  {
    "neovim/nvim-lspconfig",
    version = "*",
    lazy = false,
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

      -- Updated diagnostic config (no deprecated sign_define)
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
