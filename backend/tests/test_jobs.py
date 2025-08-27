from datetime import datetime, timedelta
import models
import jobs

def test_cleanup_inactive_devices(db_session):
    # Create data
    new_title = models.Title(slug="test-title-6", title="Test Title 6")
    db_session.add(new_title)
    db_session.commit()
    new_product = models.Product(title_id=new_title.id)
    db_session.add(new_product)
    db_session.commit()
    new_qr = models.QRCode(qr="test-qr-6", product_id=new_product.id)
    db_session.add(new_qr)
    db_session.commit()

    # Create bindings
    # Active, but old
    binding1 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device1", active=True, last_seen_at=datetime.utcnow() - timedelta(days=100))
    # Active and recent
    binding2 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device2", active=True, last_seen_at=datetime.utcnow() - timedelta(days=10))
    # Inactive already
    binding3 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device3", active=False, last_seen_at=datetime.utcnow() - timedelta(days=100))
    # Active, no last_seen_at (should not be deactivated)
    binding4 = models.DeviceBinding(qr_code_id=new_qr.id, device_id="device4", active=True, last_seen_at=None)

    db_session.add_all([binding1, binding2, binding3, binding4])
    db_session.commit()

    # Run the job
    jobs.cleanup_inactive_devices(db=db_session)

    # Check the results
    db_session.refresh(binding1)
    assert binding1.active is False # Should be deactivated

    db_session.refresh(binding2)
    assert binding2.active is True # Should still be active

    db_session.refresh(binding3)
    assert binding3.active is False # Should still be inactive

    db_session.refresh(binding4)
    assert binding4.active is True # Should still be active
