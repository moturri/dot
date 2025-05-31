return {
  "vinnymeller/swagger-preview.nvim",
  version = "*",
  build = "npm install -g swagger-ui-watcher",
  config = function()
    require("swagger-preview").setup({
      -- Optional configs can go here if needed in the future
    })

    vim.keymap.set("n", "<leader>sp", "<cmd>SwaggerPreview<CR>", { desc = "Open Swagger Preview" })
  end,
}
