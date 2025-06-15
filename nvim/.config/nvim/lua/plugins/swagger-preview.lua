return {
  "vinnymeller/swagger-preview.nvim",
  build = "npm install -g swagger-ui-watcher",
  config = function()
    require("swagger-preview").setup({})

    vim.keymap.set("n", "<leader>sp", "<cmd>SwaggerPreview<CR>", { desc = "Open Swagger Preview" })
  end,
}
