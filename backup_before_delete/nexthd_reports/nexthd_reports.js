frappe.pages['nexthd-reports'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'NextHD Reports',
        single_column: true
    });

    $(page.body).html(`
        <div class="row">

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Tiket%20per%20Bulan"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Tiket per Bulan</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Tiket%20per%20Agent"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Tiket per Agent</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Tiket%20per%20Prioritas"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Tiket per Prioritas</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Tiket%20per%20Kategori"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Tiket per Kategori</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/SLA%20Compliance%20Bulanan"
                   class="card p-3 text-decoration-none">
                    <h4>📊 SLA Compliance Bulanan</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Aset%20Bermasalah"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Aset Bermasalah</h4>
                </a>
            </div>

            <div class="col-md-4 mb-3">
                <a href="/app/query-report/Detail%20Tiket%20Lengkap"
                   class="card p-3 text-decoration-none">
                    <h4>📊 Detail Tiket Lengkap</h4>
                </a>
            </div>

        </div>
    `);
};
