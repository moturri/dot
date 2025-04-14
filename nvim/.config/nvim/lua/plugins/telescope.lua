return {
  {
    "nvim-telescope/telescope-ui-select.nvim",
  },
  {
    "nvim-telescope/telescope.nvim",
    tag = "0.1.5",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      local telescope = require("telescope")
      local actions = require("telescope.actions")
      local themes = require("telescope.themes")

      telescope.setup({
        defaults = {
          prompt_prefix = "󰱼 ",
          selection_caret = "➜ ",
          entry_prefix = "  ",
          initial_mode = "insert",
          sorting_strategy = "ascending",
          layout_strategy = "flex",
          layout_config = {
            horizontal = { mirror = false },
            vertical = { mirror = false },
            flex = { flip_columns = 150 },
          },
          mappings = {
            i = {
              ["<C-n>"] = actions.move_selection_next,
              ["<C-p>"] = actions.move_selection_previous,
              ["<C-c>"] = actions.close,
              ["<C-u>"] = actions.preview_scrolling_up,
              ["<C-d>"] = actions.preview_scrolling_down,
            },
            n = {
              ["<C-c>"] = actions.close,
              ["<C-j>"] = actions.move_selection_next,
              ["<C-k>"] = actions.move_selection_previous,
            },
          },
        },
        extensions = {
          ["ui-select"] = themes.get_dropdown({}),
        },
      })

      -- Load extensions
      telescope.load_extension("ui-select")

      -- Keybindings
      local builtin = require("telescope.builtin")
      -- vim.keymap.set("n", "<leader>ff", function()
      -- builtin.find_files({ hidden = true }) -- Show dotfiles
      -- end, { desc = "Find Files (including dotfiles)" })
      vim.keymap.set("n", "<leader>ff", builtin.find_files, { desc = "Find Files" })
      vim.keymap.set("n", "<leader>fg", builtin.live_grep, { desc = "Live Grep" })
      vim.keymap.set("n", "<leader>fb", builtin.buffers, { desc = "List Buffers" })
      vim.keymap.set("n", "<leader>fh", builtin.help_tags, { desc = "Help Tags" })
      vim.keymap.set("n", "<leader>fc", builtin.commands, { desc = "Commands" })
      vim.keymap.set("n", "<leader>fm", builtin.man_pages, { desc = "Man Pages" })
      vim.keymap.set("n", "<leader>fr", builtin.registers, { desc = "Registers" })
      vim.keymap.set("n", "<leader>fs", builtin.search_history, { desc = "Search History" })
      vim.keymap.set("n", "<leader>ft", builtin.tags, { desc = "Tags" })
      vim.keymap.set(
        "n",
        "<leader>f/",
        builtin.current_buffer_fuzzy_find,
        { desc = "Fuzzy Find in Current Buffer" }
      )
    end,
  },
}
