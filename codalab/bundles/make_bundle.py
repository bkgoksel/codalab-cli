import os

from codalab.bundles.named_bundle import NamedBundle
from codalab.common import State


class MakeBundle(NamedBundle):
  BUNDLE_TYPE = 'make'
  NAME_LENGTH = 8

  @classmethod
  def construct(cls, uuid_targets, targets=None):
    uuid = cls.generate_uuid()
    # Compute metadata with default values for name and description.
    targets = targets or uuid_targets
    description = 'Package containing %s' % (
      ', '.join(
        '%s:%s' % (key, os.path.join(*[part for part in target if part]))
        for (key, target) in sorted(targets.iteritems())
      ),
    )
    metadata = {
      'name': 'make-%s' % (uuid[:cls.NAME_LENGTH],),
      'description': description,
      'tags': [],
    }
    # List the dependencies of this bundle on its targets.
    dependencies = []
    for (child_path, (parent_uuid, parent_path)) in uuid_targets.iteritems():
      dependencies.append({
        'child_uuid': uuid,
        'child_path': child_path,
        'parent_uuid': parent_uuid,
        'parent_path': parent_path,
      })
    return cls({
      'uuid': uuid,
      'bundle_type': cls.BUNDLE_TYPE,
      'command': None,
      'data_hash': None,
      'state': State.CREATED,
      'metadata': metadata,
      'dependencies': dependencies,
    })

  def run(self, bundle_store, parent_dict):
    temp_dir = self.symlink_dependencies(bundle_store, parent_dict)
    return bundle_store.upload(temp_dir, allow_symlinks=True)
