using System.Windows.Controls;
using TT_PPID_CS.UI.ViewModels;

namespace TT_PPID_CS.UI.Views
{
    public partial class UserManagementView : UserControl
    {
        public UserManagementView(UserManagementViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }
    }
}
