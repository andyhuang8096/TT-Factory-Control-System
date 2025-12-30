using System.Windows.Controls;
using TT_PPID_CS.UI.ViewModels;

namespace TT_PPID_CS.UI.Views
{
    public partial class StatisticsView : UserControl
    {
        public StatisticsView(StatisticsViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }
    }
}
