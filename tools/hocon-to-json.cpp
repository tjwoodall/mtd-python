#include <hocon/config.hpp>

#include <jsoncpp/json/value.h>
#include <jsoncpp/json/writer.h>

#include <fstream>
#include <memory>
#include <exception>

Json::Value hocon_to_json(const std::shared_ptr<const hocon::config_value>& val) {
  using namespace hocon;
  switch (val->value_type()) {
    case config_value::type::OBJECT:
      {
        auto obj = std::static_pointer_cast<const config_object>(val);
        Json::Value result(Json::objectValue);
        for (const auto& member : *obj) {
          result[member.first] = hocon_to_json(member.second);
        }
        return result;
      }

    case config_value::type::LIST:
      {
        auto lst = std::static_pointer_cast<const config_list>(val);
        Json::Value result(Json::arrayValue);
        for (const auto& elem : *lst) {
          result.append(hocon_to_json(elem));
        }
        return result;
      }
    case config_value::type::STRING:
        return Json::Value(boost::get<std::string>(val->unwrapped()));
    case config_value::type::NUMBER:
      {
        auto num = val->unwrapped();
        if (boost::get<int64_t>(&num))
          return Json::Value((Json::Int64)boost::get<int64_t>(num));

        if (boost::get<int>(&num))
          return Json::Value((Json::Int64)boost::get<int>(num));

        return Json::Value(boost::get<double>(num));
      }

    case config_value::type::BOOLEAN:
      return Json::Value(boost::get<bool>(val->unwrapped()));

    case config_value::type::CONFIG_NULL:
      return Json::Value(Json::nullValue);

    default:
      throw std::runtime_error("Unsupported HOCON type");
  }
}

int main(int argc, char* argv[]) {
  if (argc < 3) {
    std::cerr << "Usage: " << argv[0] << " <output> <config.conf> ..." << std::endl;
    return 1;
  }
  int i = 2;
  Json::Value all_config;

  try {
    while (i < argc) {
      std::ifstream file(argv[i]);
      if (!file.is_open()) {
        std::cerr << "Error opening " << argv[i] << std::endl;
        return 1;
      }

      std::string line;
      std::stringstream preprocessed_content;

      Json::Value play_modules(Json::arrayValue);

      // For reasons that I don't fully understand, hocon-cpp cannot cope with
      // 'play.modules.enabled +=' that appears more than 3 times in a config
      // file. So we process that separately.
      while (std::getline(file, line)) {
        if (line.find("play.modules.enabled") < line.find("#")) {

          auto start = line.find("\"");
          auto end = line.rfind("\"");
          std::string value = line.substr(start+1, end - start - 1);
          play_modules.append(value);
          line = "#" + line;
        }
        preprocessed_content << line << std::endl;
      }

      auto config = hocon::config::parse_string(preprocessed_content.str());
      auto resolved = config->resolve();
      all_config[argv[i]] = hocon_to_json(resolved->root());
      all_config[argv[i]]["play"]["modules"]["enabled"] = play_modules;
      i++;
    }

    Json::StreamWriterBuilder writerBuilder;
    writerBuilder["indentation"] = "  ";  // pretty indent

    std::unique_ptr<Json::StreamWriter> writer(writerBuilder.newStreamWriter());
    std::ofstream output(argv[1]);
    writer->write(all_config, &output);
    output << std::endl;
  } catch (std::exception& e) {
    std::cerr << "Processing " << argv[i] << std::endl;
    std::cerr << "Error converting HOCON to JSON: " << e.what() << std::endl;
    return 2;
  }

  return 0;
}
