using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.EntityFrameworkCore;
using TT_PPID_CS.Infrastructure.Persistence;
using TT_PPID_CS.Domain.Interfaces;
using TT_PPID_CS.Infrastructure.Repositories;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Application.Services;
using TT_PPID_CS.Infrastructure.Services;
using TT_PPID_CS.UI.Views;
using TT_PPID_CS.UI.ViewModels;
using System.Configuration;

namespace TT_PPID_CS.UI
{
    public partial class App : System.Windows.Application
    {
        private ServiceProvider _serviceProvider;

        public App()
        {
            ServiceCollection services = new ServiceCollection();
            ConfigureServices(services);
            _serviceProvider = services.BuildServiceProvider();
        }

        private void ConfigureServices(ServiceCollection services)
        {
            // Database
            string connectionString = "Server=192.168.30.254,1433;Database=PPID_DB;User Id=TGUser;Password=Ydse%32gr7e#;Encrypt=True;TrustServerCertificate=True;";
            services.AddDbContext<AppDbContext>(options =>
                options.UseSqlServer(connectionString), ServiceLifetime.Transient);

            // Architecture layers
            services.AddTransient<IUnitOfWork, UnitOfWork>();
            services.AddSingleton<IAuthService, AuthService>(); // AuthService holds state (CurrentUser), so Singleton is appropriate
            services.AddTransient<IPPIDService, PPIDService>();
            services.AddTransient<IImportService, ImportService>();
            services.AddTransient<IBackupService, BackupService>();
            services.AddTransient<IUserService, UserService>();
            services.AddTransient<IReportService, ReportService>();

            // ViewModels
            services.AddSingleton<MainViewModel>();
            services.AddTransient<LoginViewModel>();
            services.AddTransient<PPIDManagementViewModel>();
            services.AddTransient<UserManagementViewModel>();
            services.AddTransient<StatisticsViewModel>();

            // Views
            services.AddSingleton<MainWindow>();
            services.AddTransient<LoginWindow>();
            services.AddTransient<PPIDManagementView>();
            services.AddTransient<UserManagementView>();
            services.AddTransient<StatisticsView>();
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            var loginWindow = _serviceProvider.GetRequiredService<LoginWindow>();
            if (loginWindow.ShowDialog() == true)
            {
                var mainWindow = _serviceProvider.GetRequiredService<MainWindow>();
                mainWindow.Show();
            }
            else
            {
                Shutdown();
            }
        }
    }
}
