using System.Windows.Controls;
using TT_PPID_CS.UI.ViewModels;

namespace TT_PPID_CS.UI.Views
{
    public partial class PPIDManagementView : UserControl
    {
        public PPIDManagementView(PPIDManagementViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }
    }
}
