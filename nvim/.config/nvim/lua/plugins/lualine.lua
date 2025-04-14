return {
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "kyazdani42/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = {
          icons_enabled = true,
          theme = "auto",
          component_separators = { left = "", right = "" },
          section_separators = { left = "", right = "" },
          disabled_filetypes = {
            statusline = { "NvimTree", "packer", "Telescope" },
            winbar = {},
          },
          ignore_focus = {},
          always_divide_middle = true,
          globalstatus = true,
          refresh = {
            statusline = 100,
            tabline = 100,
            winbar = 100,
          },
        },
        sections = {
          lualine_a = { "mode" },
          lualine_b = {
            "branch",
            "diff",
            {
              "diagnostics",
              sources = { "nvim_lsp", "nvim_diagnostic" },
              sections = { "error", "warn", "info", "hint" },
              diagnostics_color = {
                error = "DiagnosticError",
                warn = "DiagnosticWarn",
                info = "DiagnosticInfo",
                hint = "DiagnosticHint",
              },
              symbols = { error = " ", warn = " ", info = " ", hint = " " },
            },
            {
              "lsp_progress",
              display_components = { "spinner", "title", "message" },
              spinner_symbols = { "⠋", "⠙", "⠹", "⠸", "⠰", "⠆", "⠇", "⠘", "⠊" },
            },
          },
          lualine_c = {
            "filename",
            {
              "lsp_progress",
              display_components = { "spinner" },
              spinner_symbols = { "⠋", "⠙", "⠹", "⠸", "⠰", "⠆", "⠇", "⠘", "⠊" },
            },
          },
          lualine_x = {
            "encoding",
            "fileformat",
            "filetype",
            {
              "python_env",
              color = { fg = "#ff8700", bg = "#282828", gui = "bold" },
              cond = function()
                return vim.bo.filetype == "python"
              end,
            },
            {
              "node_version",
              cond = function()
                return vim.fn.executable("node") == 1
              end,
              color = { fg = "#7ebf7f", bg = "#282828", gui = "italic" },
            },
          },
          lualine_y = {
            "progress",
          },
          lualine_z = { "location" },
        },
        inactive_sections = {
          lualine_a = {},
          lualine_b = {},
          lualine_c = { "filename" },
          lualine_x = { "location" },
          lualine_y = {},
          lualine_z = {},
        },
        tabline = {
          lualine_a = { "buffers" },
          lualine_b = { "branch" },
          lualine_c = {},
          lualine_x = {},
          lualine_y = {},
          lualine_z = { "tabs" },
        },
        winbar = {},
        inactive_winbar = {},
        extensions = {
          "nvim-tree",
          "quickfix",
        },
      })
    end,
  },
}
