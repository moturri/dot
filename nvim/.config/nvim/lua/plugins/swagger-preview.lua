return {
  "vinnymeller/swagger-preview.nvim",
  version = "*",
  build = "npm install -g swagger-ui-watcher",
  config = function()
    vim.keymap.set("n", "<leader>sp", "<cmd>SwaggerPreview<CR>", { desc = "Open Swagger Preview" })
  end,
}
