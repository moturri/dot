return {
  {
    "nvim-lualine/lualine.nvim",
    lazy = true,
    event = "BufReadPost",
    dependencies = {
      "kyazdani42/nvim-web-devicons",
      "j-hui/fidget.nvim",
    },
    opts = function()
      local fidget_utils
      local has_fidget, fidget = pcall(require, "fidget")
      if has_fidget then
        fidget.setup({})
        local ok, utils = pcall(require, "fidget.progress")
        if ok then fidget_utils = utils end
      end

      local has_node = vim.fn.executable("node") == 1

      -- LSP progress component
      local function fidget_status()
        if not fidget_utils then return "" end
        local msg = fidget_utils.get_progress_message()
        return msg and msg.title or ""
      end

      -- Python virtual environment
      local function python_env()
        if vim.bo.filetype ~= "python" then return "" end
        local env = vim.fn.getenv("VIRTUAL_ENV")
        return env ~= "" and "🐍 " .. env:match("^.+/(.+)$") or ""
      end

      -- Node.js version
      local function node_version()
        local ft = vim.bo.filetype
        if not (has_node and (ft == "javascript" or ft == "typescript" or ft:match("react$"))) then
          return ""
        end
        local handle = io.popen("node -v 2>/dev/null")
        if not handle then return "" end
        local version = handle:read("*a") or ""

        handle:close()
        return version:gsub("\n", "")
      end

      return {
        options = {
          icons_enabled = true,
          theme = "sequoia",
          component_separators = { left = "", right = "" },
          section_separators = { left = "", right = "" },
          disabled_filetypes = {
            statusline = { "NvimTree", "lazy", "TelescopePrompt", "alpha", "Outline" },
          },
          always_divide_middle = true,
          globalstatus = true,
        },

        sections = {
          lualine_a = { { "mode", icon = "" } },
          lualine_b = {
            { "branch", icon = "" },
            {
              "diff",
              symbols = { added = "󰐗 ", modified = "󰛿 ", removed = "󰍶 " },
              colored = true,
            },
            {
              "diagnostics",
              sources = { "nvim_lsp" },
              symbols = {
                error = " ",
                warn = " ",
                info = " ",
                hint = " ",
              },
            },
          },
          lualine_c = {
            {
              "filename",
              file_status = true,
              path = 1,
              symbols = {
                modified = " 󰐗",
                readonly = " ",
                unnamed = "[No Name]",
              },
            },
            fidget_status,
          },
          lualine_x = {
            "filetype",
            {
              "encoding",
              cond = function() return vim.bo.fileencoding ~= "utf-8" end,
            },
            "fileformat",
            python_env,
            node_version,
          },
          lualine_y = { "progress" },
          lualine_z = { "location" },
        },

        inactive_sections = {
          lualine_c = { "filename" },
          lualine_x = { "location" },
        },

        tabline = {
          lualine_a = {
            {
              "buffers",
              max_length = function()
                return math.floor(vim.o.columns * 0.7)
              end,
              filetype_names = {
                NvimTree = "File Explorer",
                fugitive = "Git",
                toggleterm = "Terminal",
              },
              show_filename_only = true,
              symbols = {
                modified = " 󰐗",
                readonly = " ",
              },
            },
          },
          lualine_b = { "branch" },
          lualine_z = {
            {
              "tabs",
              cond = function()
                return #vim.api.nvim_list_tabpages() > 1
              end,
            },
          },
        },

        extensions = {
          "nvim-tree",
          "quickfix",
          "lazy",
        },
      }
    end,
    config = function(_, opts)
      require("lualine").setup(opts)
    end,
  },
}
