---@diagnostic disable: undefined-global

return {
	"mfussenegger/nvim-dap",
	dependencies = {
		"rcarriga/nvim-dap-ui",
		"nvim-neotest/nvim-nio",
		"theHamsta/nvim-dap-virtual-text",
		{
			"jay-babu/mason-nvim-dap.nvim",
			config = function()
				require("mason-nvim-dap").setup({
					ensure_installed = { "python", "codelldb", "delve" },
					automatic_installation = true,
				})
			end,
		},
	},
	config = function()
		local dap = require("dap")
		local dapui = require("dapui")

		require("nvim-dap-virtual-text").setup()
		dapui.setup()

		dap.listeners.after.event_initialized["dapui_config"] = function()
			dapui.open()
		end
		dap.listeners.before.event_terminated["dapui_config"] = function()
			dapui.close()
		end
		dap.listeners.before.event_exited["dapui_config"] = function()
			dapui.close()
		end

		local map = vim.keymap.set
		map("n", "<Leader>db", dap.toggle_breakpoint, { desc = "Toggle Breakpoint" })
		map("n", "<Leader>dc", dap.continue, { desc = "Continue" })
		map("n", "<Leader>di", dap.step_into, { desc = "Step Into" })
		map("n", "<Leader>do", dap.step_over, { desc = "Step Over" })
		map("n", "<Leader>dO", dap.step_out, { desc = "Step Out" })
		map("n", "<Leader>dr", dap.repl.open, { desc = "Open REPL" })
		map("n", "<Leader>dl", dap.run_last, { desc = "Run Last" })
		map("n", "<Leader>du", dapui.toggle, { desc = "Toggle DAP UI" })
		map("n", "<Leader>ds", function()
			dapui.float_element("scopes")
		end, { desc = "Float Scopes" })
		map("n", "<Leader>df", function()
			dapui.float_element("repl", { enter = true })
		end, { desc = "Float REPL" })
	end,
}
