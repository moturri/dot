return {
  -- Mason Setup
  {
    "williamboman/mason.nvim",
    version = "*",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      require("mason").setup({
        ui = { border = "rounded" },
      })

      if pcall(require, "fidget") then
        require("fidget").setup({})
      else
        vim.notify("Fidget plugin not found.")
      end
    end,
  },

  -- Mason-LSPConfig Setup
  {
    "williamboman/mason-lspconfig.nvim",
    version = "*",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      automatic_installation = true,
    },
  },

  -- LSPConfig Setup
  {
    "neovim/nvim-lspconfig",
    version = "*",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      local lspconfig = require("lspconfig")
      local mason_lspconfig = require("mason-lspconfig")

      local capabilities = vim.lsp.protocol.make_client_capabilities()
      local has_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
      if has_cmp then
        capabilities = cmp_nvim_lsp.default_capabilities()
      end

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

        if client.server_capabilities.documentSymbolProvider then
          local ok, navic = pcall(require, "nvim-navic")
          if ok then
            navic.attach(client, bufnr)
          end
        end
      end

      -- Define diagnostic signs
      local signs = { Error = "", Warn = "", Hint = "", Info = "" }
      for type, icon in pairs(signs) do
        local hl = "DiagnosticSign" .. type
        vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = "" })
      end

      vim.diagnostic.config({
        virtual_text = true,
        underline = true,
        update_in_insert = false,
        severity_sort = true,
      })

      local default_config = {
        on_attach = on_attach,
        capabilities = capabilities,
      }

      for _, server in ipairs(mason_lspconfig.get_installed_servers()) do
        lspconfig[server].setup(default_config)
      end
    end,
  },
}
