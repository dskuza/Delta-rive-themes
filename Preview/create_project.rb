#!/usr/bin/env ruby
# Regenerate only this self-contained preview project. Requires xcodeproj (CocoaPods).
require 'xcodeproj'
require 'pathname'
Dir.chdir(__dir__)
p = Xcodeproj::Project.new('RiveControllerPreview.xcodeproj')
app = p.new_target(:application, 'RiveControllerPreview', :ios, '17.4')
app.build_configurations.each do |config|
  config.build_settings.merge!('PRODUCT_BUNDLE_IDENTIFIER' => 'com.delta.RiveControllerPreview', 'SWIFT_VERSION' => '5.0', 'GENERATE_INFOPLIST_FILE' => 'YES', 'INFOPLIST_KEY_UIApplicationSceneManifest_Generation' => 'YES', 'INFOPLIST_KEY_UILaunchScreen_Generation' => 'YES', 'INFOPLIST_KEY_UISupportedInterfaceOrientations' => 'UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight', 'TARGETED_DEVICE_FAMILY' => '1,2', 'CODE_SIGNING_ALLOWED' => 'NO')
end
sources = p.main_group.new_group('Sources')
app.source_build_phase.add_file_reference(sources.new_file('App.swift'))
Dir.glob('../../../Delta/Controller Themes/*.swift').sort.each { |path| app.source_build_phase.add_file_reference(sources.new_file(path)) }
resources = p.main_group.new_group('Resources')
['../Dist/Template.deltaskin', '../Dist/NeonCircuit.deltaskin', '../Dist/Orbit.deltaskin', '../Dist/OrbitCrystal.deltaskin', '../../NESInputTest/input-test.nes', '../../N64InputTest/mimi-6126231.z64', '../../N64InputTest/LICENSE.mimi'].each { |path| app.resources_build_phase.add_file_reference(resources.new_file(path)) }
embed = app.new_copy_files_build_phase('Embed Frameworks')
embed.dst_subfolder_spec = '10'
['DeltaCore', 'NESDeltaCore', 'N64DeltaCore'].each do |name|
  path = "../../../Cores/#{name}/#{name}.xcodeproj"
  ref = p.main_group.new_file(path)
  subproject = Xcodeproj::Project.open(path)
  app.add_dependency(subproject.targets.find { |target| target.name == name })
  products = p.root_object.project_references.find { |r| r[:project_ref] == ref }[:product_group]
  product = products.children.find { |child| child.path == "#{name}.framework" }
  app.frameworks_build_phase.add_file_reference(product)
  embed.add_file_reference(product).settings = { 'ATTRIBUTES' => ['CodeSignOnCopy', 'RemoveHeadersOnCopy'] }
  if name == 'N64DeltaCore'
    ['N64DeltaCore_Video', 'N64DeltaCore_RSP'].each do |plugin|
      app.add_dependency(subproject.targets.find { |target| target.product_reference.path == "#{plugin}.framework" })
      product = products.children.find { |child| child.path == "#{plugin}.framework" }
      app.frameworks_build_phase.add_file_reference(product)
      embed.add_file_reference(product).settings = { 'ATTRIBUTES' => ['CodeSignOnCopy', 'RemoveHeadersOnCopy'] }
    end
  end
end
zip = p.frameworks_group.new_file('ZIPFoundation.framework', :built_products)
app.frameworks_build_phase.add_file_reference(zip)
embed.add_file_reference(zip).settings = { 'ATTRIBUTES' => ['CodeSignOnCopy', 'RemoveHeadersOnCopy'] }
rive = p.new(Xcodeproj::Project::Object::XCRemoteSwiftPackageReference)
rive.repositoryURL = 'https://github.com/rive-app/rive-ios'
rive.requirement = { 'kind' => 'exactVersion', 'version' => '6.29.0' }
p.root_object.package_references << rive
product = p.new(Xcodeproj::Project::Object::XCSwiftPackageProductDependency)
product.package = rive
product.product_name = 'RiveRuntime'
app.package_product_dependencies << product
build_file = p.new(Xcodeproj::Project::Object::PBXBuildFile)
build_file.product_ref = product
app.frameworks_build_phase.files << build_file
tests = p.new_target(:ui_test_bundle, 'ControllerThemeUITests', :ios, '17.4')
tests.source_build_phase.add_file_reference(sources.new_file('ControllerThemeUITests.swift'))
tests.add_dependency(app)
tests.build_configurations.each do |config|
  config.build_settings.merge!('PRODUCT_BUNDLE_IDENTIFIER' => 'com.delta.ControllerThemeUITests', 'SWIFT_VERSION' => '5.0', 'GENERATE_INFOPLIST_FILE' => 'YES', 'TEST_TARGET_NAME' => 'RiveControllerPreview', 'CODE_SIGNING_ALLOWED' => 'NO')
end
p.save
scheme = Xcodeproj::XCScheme.new
scheme.add_build_target(app)
scheme.add_test_target(tests)
scheme.set_launch_target(app)
scheme.save_as(p.path, 'RiveControllerPreview', true)
