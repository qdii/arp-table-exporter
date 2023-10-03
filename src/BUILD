load("@pip_deps//:requirements.bzl", "requirement")

py_binary(
  name="arp_table_exporter",
  srcs=["arp_table_exporter.py"],
  deps=[
    requirement("absl-py"),
    requirement("freezegun"),
    requirement("prometheus-client"),
    requirement("python-dateutil"),
    requirement("six"),
  ],
)

py_test(
  name="arp_table_exporter_test",
  srcs=["arp_table_exporter_test.py"],
  deps=[
    ":arp_table_exporter",
  ],
)
