C:\Users\GavithGethmin\Desktop>python main.py

[1/22] Visiting: https://pastpapers.wiki/north-central-province-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1
Found direct .pdf link with wpfd_downloadlink class
→ Clicking download → Saving as: North_Central_Province_-_2023_Grade_13_Physics_1st_Term_-_Sinhalapdf.pdf
✓ Success! Saved → physics_2023_grade13_papers\North_Central_Province_-_2023_Grade_13_Physics_1st_Term_-_Sinhalapdf.pdf

[2/22] Visiting: https://pastpapers.wiki/visakha-vidyalaya-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1
Found direct .pdf link with wpfd_downloadlink class
→ Clicking download → Saving as: Visakha_Vidyalaya_-_2023_Grade_13_Physics_1st_Term_-_Sinhalapdf.pdf
Traceback (most recent call last):
  File "C:\Users\GavithGethmin\Desktop\main.py", line 127, in <module>
    download.save_as(full_path)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "C:\Users\GavithGethmin\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\playwright\sync_api\_generated.py", line 7379, in save_as
    return mapping.from_maybe_impl(self._sync(self._impl_obj.save_as(path=path)))
                                   ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\GavithGethmin\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\playwright\_impl\_sync_base.py", line 113, in _sync
    self._dispatcher_fiber.switch()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\GavithGethmin\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\playwright\sync_api\_context_manager.py", line 56, in greenlet_main
    self._loop.run_until_complete(self._connection.run_as_sync())
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 712, in run_until_complete
    self.run_forever()
    ~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 683, in run_forever
    self._run_once()
    ~~~~~~~~~~~~~~^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 2012, in _run_once
    event_list = self._selector.select(timeout)
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\windows_events.py", line 446, in select
    self._poll(timeout)
    ~~~~~~~~~~^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\windows_events.py", line 775, in _poll
    status = _overlapped.GetQueuedCompletionStatus(self._iocp, ms)
KeyboardInterrupt
Future exception was never retrieved
future: <Future finished exception=TargetClosedError('Target page, context or browser has been closed')>
playwright._impl._errors.TargetClosedError: Target page, context or browser has been closed
^C
