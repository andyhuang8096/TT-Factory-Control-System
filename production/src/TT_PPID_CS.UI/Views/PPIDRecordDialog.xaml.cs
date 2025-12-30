using System.Windows;
using TT_PPID_CS.UI.ViewModels;

namespace TT_PPID_CS.UI.Views
{
    public partial class PPIDRecordDialog : Window
    {
        public PPIDRecordDialog(PPIDRecordViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            // Simple validation
            if (DataContext is PPIDRecordViewModel vm)
            {
                if (string.IsNullOrWhiteSpace(vm.Record.PPID))
                {
                    MessageBox.Show("PPID 不能为空", "验证错误", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
            }

            DialogResult = true;
            Close();
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
