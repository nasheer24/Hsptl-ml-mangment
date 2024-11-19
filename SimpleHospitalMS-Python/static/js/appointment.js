$(document).ready(function () {
    var table;

    function addAppointment(data) {
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "appointment",
            "method": "POST",
            "headers": {
                "content-type": "application/json",
                "cache-control": "no-cache"
            },
            "processData": false,
            "data": JSON.stringify(data)
        };

        $.ajax(settings).done(function (response) {
            $.notify("Appointment has been added successfully!", {"status": "success"});
            $('.modal.in').modal('hide');
            table.destroy();
            $('#datatable4 tbody').empty(); // empty in case the columns change
            getAppointment();
        });
    }

    function deleteAppointment(id) {
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "appointment/" + id,
            "method": "DELETE",
            "headers": {
                "cache-control": "no-cache"
            }
        };

        swal({
            title: "Are you sure?",
            text: "You will not be able to recover this data",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete it!",
            closeOnConfirm: false
        }, function () {
            $.ajax(settings).done(function (response) {
                swal("Deleted!", "Appointment has been cancelled.", "success");
                table.destroy();
                $('#datatable4 tbody').empty(); // empty in case the columns change
                getAppointment();
            });
        });
    }

    function getAppointment() {
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "appointment",
            "method": "GET",
            "headers": {
                "cache-control": "no-cache"
            }
        };

        $.ajax(settings).done(function (response) {
            for (i = 0; i < response.length; i++) {
                response[i].pat_fullname = response[i].pat_first_name + " " + response[i].pat_last_name;
                response[i].doc_fullname = response[i].doc_first_name + " " + response[i].doc_last_name;
            }

            table = $('#datatable4').DataTable({
                "bDestroy": true,
                'paging': true, // Table pagination
                'ordering': true, // Column ordering
                'info': true, // Bottom left status text
                aaData: response,
                "aaSorting": [],
                aoColumns: [
                    { mData: 'doc_fullname' },
                    { mData: 'pat_fullname' },
                    { mData: 'appointment_date' },
                    {
                        mRender: function (o, type, row) {
                            return `
                                <button class="btn-xs btn btn-danger delete-btn" type="button" style="border-radius:0%;">Remove</button>
                                <button class="btn-xs btn btn-info bill-btn" type="button" style="border-radius:0%;">Bill</button>
                            `;
                        }
                    }
                ]
            });

            $('#datatable4 tbody').on('click', '.delete-btn', function () {
                var data = table.row($(this).parents('tr')).data();
                deleteAppointment(data.app_id);
            });

            $('#datatable4 tbody').on('click', '.bill-btn', function () {
                var data = table.row($(this).parents('tr')).data();
                window.location.href = `bill.html?id=${data.app_id}`;
            });
        });
    }

    $("#addpatient").click(function () {
        $('#myModal').modal().one('shown.bs.modal', function (e) {
            $("#doctor_select").html(doctorSelect);
            $("#patient_select").html(patientSelect);

            $(".form_datetime").datetimepicker({
                format: 'yyyy-mm-dd hh:ii:ss',
                startDate: new Date(),
                initialDate: new Date()
            });

            $("#savethepatient").off("click").on("click", function (e) {
                var instance = $('#detailform').parsley();
                instance.validate();
                if (instance.isValid()) {
                    var jsondata = $('#detailform').serializeJSON();
                    addAppointment(jsondata);
                }
            });
        });
    });

    var doctorSelect = "";
    function getDoctor() {
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "doctor",
            "method": "GET",
            "headers": {
                "cache-control": "no-cache"
            }
        };

        $.ajax(settings).done(function (response) {
            for (i = 0; i < response.length; i++) {
                response[i].doc_fullname = response[i].doc_first_name + " " + response[i].doc_last_name;
                doctorSelect += `<option value=${response[i].doc_id}>${response[i].doc_fullname}</option>`;
            }
        });
    }

    var patientSelect = "";
    function getPatient() {
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "patient",
            "method": "GET",
            "headers": {
                "cache-control": "no-cache"
            }
        };

        $.ajax(settings).done(function (response) {
            for (i = 0; i < response.length; i++) {
                response[i].pat_fullname = response[i].pat_first_name + " " + response[i].pat_last_name;
                patientSelect += `<option value=${response[i].pat_id}>${response[i].pat_fullname}</option>`;
            }
        });
    }

    getDoctor();
    getPatient();
    getAppointment();
});
