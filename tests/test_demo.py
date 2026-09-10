from plumbing.demo import main


def test_offline_demo_completes_booking_lifecycle(capsys):
    main()
    output = capsys.readouterr().out
    assert 'Invalid phone rejected:' in output
    assert 'Retry returned same booking: True' in output
    assert 'Active appointments: 1' in output
    assert 'Cancelled: 100001; available slots: 9' in output
